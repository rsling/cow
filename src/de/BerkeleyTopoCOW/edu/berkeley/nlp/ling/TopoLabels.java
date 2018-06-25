package edu.berkeley.nlp.ling;

import java.util.ArrayList;

/**
 * A list of labels that should be printed when generating XML-like output.
 * All other labels will NOT appear in the output (currently, all POS tags).
 * 
 * @author Felix Bildhauer
 *
 */

public class TopoLabels {

	private static ArrayList<String> topofields = new ArrayList<String>();
	
	static boolean checkLabel(String someLabel){
	    topofields.add("SIMPX");
	    topofields.add("ADJX");
	    topofields.add("ADVX");
	    topofields.add("C");
	    topofields.add("DM");
	    topofields.add("DP");
	    topofields.add("ENADD");
	    topofields.add("FKONJ");
	    topofields.add("FKOORD");
	    topofields.add("FX");
	    topofields.add("KOORD");
	    topofields.add("LK");
	    topofields.add("LV");
	    topofields.add("MF");
	    topofields.add("MFE");
	    topofields.add("NF");
	    topofields.add("NX");
	    topofields.add("PARORD");
	    topofields.add("PSIMPX");
	    topofields.add("PX");
	    topofields.add("RSIMPX");
	    topofields.add("VC");
	    topofields.add("VCE");
	    topofields.add("VF");
	    topofields.add("VXFIN");
	    topofields.add("VXINF");
		if (topofields.contains(someLabel)) return true;
		else return false;
	} 	
	
	
	
    
    
   
}
