// Ghidra post-script for tests/static/test_decompile.py (T18): reports, for listing addresses, what
// GoalSetup.java put there. Not part of the decompile run.
//
// Arguments: <segmap.tsv written by GoalSetup.java> <output file> <SSSS:OOOO>...
//
// Per address, one line: the listing address, the Ghidra address, the function's name there (or -),
// its first 8 bytes in hex, the functions it calls (by name) and the data-segment addresses its
// instructions refer to (as listing DS offsets), each list sorted, comma-separated.

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.TreeMap;
import java.util.TreeSet;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.SegmentedAddress;
import ghidra.program.model.address.SegmentedAddressSpace;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;

public class GoalProbe extends GhidraScript {
	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		TreeMap<Integer, Integer> toGhidra = new TreeMap<>();
		int dataGhidra = -1;
		try (BufferedReader in = new BufferedReader(new FileReader(args[0]))) {
			String line = in.readLine();
			while ((line = in.readLine()) != null) {
				String[] f = line.split("\t");
				toGhidra.put(Integer.parseInt(f[0], 16), Integer.parseInt(f[1], 16));
			}
		}
		dataGhidra = toGhidra.get(0x2581);
		SegmentedAddressSpace space =
			(SegmentedAddressSpace) currentProgram.getAddressFactory().getDefaultAddressSpace();
		try (PrintWriter w = new PrintWriter(args[1])) {
			for (int k = 2; k < args.length; k++) {
				String[] so = args[k].split(":");
				int seg = Integer.parseInt(so[0], 16);
				int off = Integer.parseInt(so[1], 16);
				Address a = space.getAddress(toGhidra.get(seg), off);
				Function f = getFunctionAt(a);
				byte[] bytes = new byte[8];
				currentProgram.getMemory().getBytes(a, bytes);
				StringBuilder hex = new StringBuilder();
				for (byte b : bytes) {
					hex.append(String.format("%02X", b & 0xff));
				}
				TreeSet<String> calls = new TreeSet<>();
				TreeSet<String> data = new TreeSet<>();
				if (f != null) {
					for (Instruction i : currentProgram.getListing().getInstructions(f.getBody(),
						true)) {
						for (Reference r : i.getReferencesFrom()) {
							Address to = r.getToAddress();
							if (r.getReferenceType().isCall()) {
								Function g = getFunctionAt(to);
								calls.add(g == null ? "?" + to : g.getName());
							}
							else if (r.getReferenceType().isData() &&
								to instanceof SegmentedAddress s &&
								(s.getOffset() >> 16) == (dataGhidra >> 12)) {
								data.add(String.format("DS:%04X", s.getOffset() & 0xffff));
							}
						}
					}
				}
				w.println(args[k] + "\t" + a + "\t" + (f == null ? "-" : f.getName()) + "\t" + hex +
					"\t" + String.join(",", calls) + "\t" + String.join(",", data));
			}
		}
	}
}
