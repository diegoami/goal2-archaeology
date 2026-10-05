// Ghidra post-analysis script for tools/static/decompile.sh (T18). Not run by hand.
//
// Arguments: <segmap.tsv written by GoalSetup.java> <raw output file> <timeout seconds per function>
//
// Names every function Ghidra's analysis added after its listing address (f_SSSS_OOOO, like
// GoalSetup.java does for the routines of routines.tsv), then decompiles every function in address
// order with the default decompiler options and writes, per function, one line
//   @@FUNC <ghidra address> <name> <calling convention> <ok|failed> <error message, if failed>
// followed by the decompiled C. tools/static/decompiled.py turns that into the committed files.

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.OutputStreamWriter;
import java.io.FileOutputStream;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.TreeMap;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.SegmentedAddress;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

public class GoalDecompile extends GhidraScript {
	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		if (args.length != 3) {
			throw new IllegalArgumentException(
				"usage: GoalDecompile.java <segmap.tsv> <raw output> <timeout seconds>");
		}
		TreeMap<Integer, Integer> toListing = new TreeMap<>(); // Ghidra segment -> listing segment
		try (BufferedReader in = new BufferedReader(new FileReader(args[0]))) {
			String line = in.readLine(); // header
			while ((line = in.readLine()) != null) {
				String[] f = line.split("\t"); // listing segment, Ghidra segment, bytes
				toListing.put(Integer.parseInt(f[1], 16), Integer.parseInt(f[0], 16));
			}
		}
		int timeout = Integer.parseInt(args[2]);

		List<Function> functions = new ArrayList<>();
		for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
			functions.add(f);
		}
		int renamed = 0;
		for (Function f : functions) {
			// a name GoalAnnotate.java gave (USER_DEFINED, T20) stays; without it only f_ names are
			if (f.getName().startsWith("f_") || f.getSymbol().getSource() == SourceType.USER_DEFINED) {
				continue;
			}
			SegmentedAddress a = (SegmentedAddress) f.getEntryPoint();
			Integer seg = toListing.get(a.getSegment());
			if (seg == null) {
				throw new IllegalStateException("function outside a mapped segment: " + a);
			}
			f.setName(String.format("f_%04X_%04X", seg, a.getSegmentOffset()), SourceType.ANALYSIS);
			renamed++;
		}

		DecompInterface decompiler = openDecompiler();
		int ok = 0;
		int failed = 0;
		try (PrintWriter w = new PrintWriter(new OutputStreamWriter(
			new FileOutputStream(args[1]), StandardCharsets.UTF_8))) {
			for (Function f : functions) {
				monitor.checkCancelled();
				// A failed attempt is retried with a fresh decompiler process only when the
				// result's error message says the decompiler process died ("Decompiler process
				// died": it died once mid-run on the shared machine, 1771:602D, T18 rework).
				// Any other unsuccessful result is written as a failure at once; in the runs
				// made it failed the same way on every attempt.
				DecompileResults r = null;
				for (int attempt = 1; attempt <= ATTEMPTS; attempt++) {
					r = decompiler.decompileFunction(f, timeout, monitor);
					if (r != null && r.decompileCompleted() && r.getDecompiledFunction() != null) {
						break;
					}
					String msg = r == null ? "no result" : r.getErrorMessage();
					println("GOALRETRY " + f.getName() + " attempt " + attempt + ": " + msg);
					if (msg == null || !msg.contains("process died")) {
						break;
					}
					decompiler.dispose();
					decompiler = openDecompiler();
				}
				String head = "@@FUNC " + f.getEntryPoint() + " " + f.getName() + " " +
					f.getCallingConventionName();
				if (r != null && r.decompileCompleted() && r.getDecompiledFunction() != null) {
					w.println(head + " ok");
					w.print(r.getDecompiledFunction().getC().replace("\r", ""));
					ok++;
				}
				else {
					String msg = r == null ? "no result" : r.getErrorMessage();
					msg = msg == null || msg.isBlank() ? "no message" : msg;
					w.println(head + " failed " + msg.strip().replaceAll("\\s+", " "));
					failed++;
				}
			}
		}
		decompiler.dispose();
		println("GOALDECOMPILE functions " + functions.size() + " renamed " + renamed + " ok " + ok +
			" failed " + failed);
	}

	static final int ATTEMPTS = 3;

	DecompInterface openDecompiler() {
		DecompInterface decompiler = new DecompInterface();
		DecompileOptions options = new DecompileOptions();
		options.grabFromProgram(currentProgram);
		decompiler.setOptions(options);
		if (!decompiler.openProgram(currentProgram)) {
			throw new IllegalStateException("decompiler: " + decompiler.getLastMessage());
		}
		return decompiler;
	}
}
