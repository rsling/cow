package edu.berkeley.nlp.ling;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;

/**
 * A list of labels that should be printed when generating XML-like output.
 * All other labels will NOT appear in the output (currently, all POS tags).
 * 
 * @author Felix Bildhauer
 *
 */

public class TopoLabels {

	public static ArrayList<String> topofields = new ArrayList<String>(
			Arrays.asList("SIMPX", "ADJX", "ADVX", "C", "DM", "DP",
					     "ENADD", "FKONJ", "FKOORD", "FX", "KOORD", "LK",
					     "LV", "MF", "MFE", "NF", "NX", "PARORD", "PSIMPX",
					     "PX", "RSIMPX", "VC", "VCE", "VF", "VXFIN", "VXINF"));
	} 	
	
	
	
    

