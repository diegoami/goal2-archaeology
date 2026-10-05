// Ghidra post-analysis script for tools/static/decompile.sh --annotations (T20). Not run by hand.
//
// Arguments: <segmap.tsv written by GoalSetup.java> <annotations directory>
//
// Applies the tracked annotations of static/goal-exe/annotations/ before GoalDecompile.java runs:
//   records.tsv  one structure per record type (name, size in bytes), in the category /goal
//   fields.tsv   the fields of those structures (record, offset, name, type)
//   globals.tsv  a label and a data type per data-segment offset (DS:XXXX of segment 2581)
//   routines.tsv a name per routine (listing address SSSS:OOOO), source USER_DEFINED, so that
//                GoalDecompile.java keeps it
// The checks of tools/static/check_annotations.py run before this script; it still refuses a row
// whose address holds no function or no data segment byte.
//
// Types, as written in the annotations: byte, char, word, int16, dword, a record's name, any of
// those followed by [N] (an array) or " far*" (a 4-byte segment:offset pointer).

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.SegmentedAddressSpace;
import ghidra.program.model.data.ArrayDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CategoryPath;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DWordDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DataTypeConflictHandler;
import ghidra.program.model.data.DataTypeManager;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.StructureDataType;
import ghidra.program.model.data.WordDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

public class GoalAnnotate extends GhidraScript {
	static final int DATA_SEGMENT = 0x2581; // static/goal-exe/README.md

	TreeMap<Integer, Integer> toGhidra = new TreeMap<>(); // listing segment -> Ghidra segment
	Map<String, DataType> records = new HashMap<>();
	DataTypeManager dtm;
	SegmentedAddressSpace space;

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		if (args.length != 2) {
			throw new IllegalArgumentException("usage: GoalAnnotate.java <segmap.tsv> <annotations>");
		}
		for (String[] f : read(args[0])) { // listing segment, Ghidra segment, bytes
			toGhidra.put(Integer.parseInt(f[0], 16), Integer.parseInt(f[1], 16));
		}
		String dir = args[1];
		dtm = currentProgram.getDataTypeManager();
		space = (SegmentedAddressSpace) currentProgram.getAddressFactory().getDefaultAddressSpace();
		CategoryPath cat = new CategoryPath("/goal");

		// records first (empty), so that a field or a global may point to any of them
		Map<String, StructureDataType> structs = new HashMap<>();
		for (String[] r : read(dir + "/records.tsv")) { // name, size, basis
			StructureDataType s = new StructureDataType(cat, r[0], Integer.parseInt(r[1].substring(2), 16), dtm);
			structs.put(r[0], s);
			records.put(r[0], s);
		}
		int fields = 0;
		for (String[] r : read(dir + "/fields.tsv")) { // record, offset, name, type, confidence, basis
			StructureDataType s = structs.get(r[0]);
			DataType t = type(r[3]);
			s.replaceAtOffset(Integer.parseInt(r[1].substring(2), 16), t, t.getLength(), r[2], null);
			fields++;
		}
		for (Map.Entry<String, StructureDataType> e : structs.entrySet()) {
			records.put(e.getKey(), dtm.addDataType(e.getValue(), DataTypeConflictHandler.REPLACE_HANDLER));
		}

		int globals = 0;
		int ds = toGhidra.get(DATA_SEGMENT);
		for (String[] r : read(dir + "/globals.tsv")) { // DS offset, name, type, confidence, basis
			Address a = space.getAddress(ds, Integer.parseInt(r[0].substring(3), 16));
			if (currentProgram.getMemory().getBlock(a) == null) {
				throw new IllegalStateException("global outside the data segment: " + r[0]);
			}
			createLabel(a, r[1], true, SourceType.USER_DEFINED);
			if (!r[2].equals("-")) {
				DataType t = type(r[2]);
				clearListing(a, a.add(t.getLength() - 1));
				createData(a, t);
			}
			globals++;
		}

		int named = 0;
		for (String[] r : read(dir + "/routines.tsv")) { // address, name, purpose, confidence, basis
			String[] so = r[0].split(":");
			Address a = space.getAddress(toGhidra.get(Integer.parseInt(so[0], 16)),
				Integer.parseInt(so[1], 16));
			Function f = getFunctionAt(a);
			if (f == null) {
				throw new IllegalStateException("no function at " + r[0]);
			}
			f.setName(r[1], SourceType.USER_DEFINED);
			named++;
		}
		println("GOALANNOTATE records " + structs.size() + " fields " + fields + " globals " + globals +
			" routines " + named);
	}

	DataType type(String spec) {
		spec = spec.strip();
		if (spec.endsWith(" far*")) {
			return new PointerDataType(type(spec.substring(0, spec.length() - 5)), 4, dtm);
		}
		if (spec.endsWith("]")) {
			int open = spec.lastIndexOf('[');
			DataType e = type(spec.substring(0, open));
			int n = Integer.parseInt(spec.substring(open + 1, spec.length() - 1));
			return new ArrayDataType(e, n, e.getLength(), dtm);
		}
		switch (spec) {
			case "byte": return ByteDataType.dataType;
			case "char": return CharDataType.dataType;
			case "word": return WordDataType.dataType;
			case "int16": return ShortDataType.dataType;
			case "dword": return DWordDataType.dataType;
			default:
				DataType r = records.get(spec);
				if (r == null) {
					throw new IllegalArgumentException("unknown type " + spec);
				}
				return r;
		}
	}

	/** The rows of a TSV file: no header line, no comment (;) or blank lines. */
	static List<String[]> read(String path) throws Exception {
		List<String[]> out = new ArrayList<>();
		try (BufferedReader in = new BufferedReader(new FileReader(path))) {
			String line = in.readLine(); // header
			while ((line = in.readLine()) != null) {
				if (line.isBlank() || line.startsWith(";")) {
					continue;
				}
				out.add(line.split("\t", -1));
			}
		}
		return out;
	}
}
