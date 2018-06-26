package edu.berkeley.nlp.PCFGLA;

import edu.berkeley.nlp.PCFGLA.GrammarTrainer.Options;
import edu.berkeley.nlp.PCFGLA.smoothing.SmoothAcrossParentBits;
import edu.berkeley.nlp.PCFGLA.smoothing.SmoothAcrossParentSubstate;
import edu.berkeley.nlp.PCFGLA.smoothing.Smoother;
import edu.berkeley.nlp.io.PTBLineLexer;
import edu.berkeley.nlp.io.PTBTokenizer;
import edu.berkeley.nlp.io.PTBLexer;
import edu.berkeley.nlp.ling.StateSet;
import edu.berkeley.nlp.ling.Tree;
import edu.berkeley.nlp.ling.Trees;
import edu.berkeley.nlp.ui.TreeJPanel;
import edu.berkeley.nlp.util.CommandLineUtils;
import edu.berkeley.nlp.util.Numberer;
import edu.berkeley.nlp.util.Option;
import edu.berkeley.nlp.util.OptionParser;

import java.awt.AlphaComposite;
import java.awt.BorderLayout;
import java.awt.Graphics2D;
import java.awt.HeadlessException;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.geom.Rectangle2D;
import java.awt.image.BufferedImage;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.StringReader;
import java.util.*;
import java.util.zip.GZIPInputStream;

import javax.imageio.ImageIO;
import javax.swing.JFrame;

/**
 * Reads in the Penn Treebank and generates N_GRAMMARS different grammars.
 *
 * @author Slav Petrov
 * 
 * with minor modifications by Felix Bildhauer
 * for the COW web corpus project
 */

public class BerkeleyParser  {
	static TreeJPanel tjp;
	static JFrame frame;
	
	public static class Options {

		@Option(name = "-gr", required = true, usage = "Grammarfile (Required)\n")
		public String grFileName;

		@Option(name = "-tokenize", usage = "Tokenize input first. (Default: false=text is already tokenized)")
		public boolean tokenize;
		
		@Option(name = "-viterbi", usage = "Compute viterbi derivation instead of max-rule tree (Default: max-rule)")
		public boolean viterbi;

		@Option(name = "-binarize", usage = "Output binarized trees. (Default: false)")
		public boolean binarize;

		@Option(name = "-scores", usage = "Output inside scores (only for binarized viterbi trees). (Default: false)")
		public boolean scores;

		@Option(name = "-substates", usage = "Output subcategories (only for binarized viterbi trees). (Default: false)")
		public boolean substates;

		@Option(name = "-accurate", usage = "Set thresholds for accuracy. (Default: set thresholds for efficiency)")
		public boolean accurate;

		@Option(name = "-confidence", usage = "Output confidence measure, i.e. tree likelihood (Default: false)")
		public boolean confidence;

		@Option(name = "-likelihood", usage = "Output sentence likelihood, i.e. summing out all parse trees (Default: false)")
		public boolean likelihood;

		@Option(name = "-render", usage = "Write rendered tree to image file. (Default: false)")
		public boolean render;
		
		@Option(name = "-chinese", usage = "Enable some Chinese specific features in the lexicon.")
		public boolean chinese;

		@Option(name = "-inputFile", usage = "Read input from this file instead of reading it from STDIN.")
		public String inputFile;

		@Option(name = "-outputFile", usage = "Store output in this file instead of printing it to STDOUT.")
		public String outputFile;
	
		@Option(name = "-useGoldPOS", usage = "Read vertical text, two columns (TAB separated): token, gold POS tag")
		public boolean goldPOS;
		
		@Option(name = "-outputXML", usage = "Transform output to XML-like format, one token per line")
		public boolean outputXML;
		
		@Option(name = "-maxLength", usage = "Maximum length of sentences (default: 200 tokens). Longer sentences will simply be copied to output.")
		public int maxLength = 200;
	}
	
  @SuppressWarnings("unchecked")
	public static void main(String[] args) {
		OptionParser optParser = new OptionParser(Options.class);
		Options opts = (Options) optParser.parse(args, true);

    double threshold = 1.0;
    
    String inFileName = opts.grFileName;
    ParserData pData = ParserData.Load(inFileName);
    if (pData==null) {
      System.out.println("Failed to load grammar from file"+inFileName+".");
      System.exit(1);
    }
    Grammar grammar = pData.getGrammar();
    Lexicon lexicon = pData.getLexicon();
    Numberer.setNumberers(pData.getNumbs());
    
//    if (opts.chinese) Corpus.myTreebank = Corpus.TreeBankType.CHINESE;
    
    CoarseToFineMaxRuleParser parser = null;
 //   if (opts.kbest==1) 
    parser = new CoarseToFineMaxRuleParser(grammar, lexicon, threshold,-1,opts.viterbi,opts.substates,opts.scores, opts.accurate, false, true, true);
    //else parser = new CoarseToFineNBestParser(grammar, lexicon, opts.kbest,threshold,-1,opts.viterbi,opts.substates,opts.scores, opts.accurate, false, true, true);
    parser.binarization = pData.getBinarization();
    
    if (opts.render) tjp = new TreeJPanel();
    
 /*   MultiThreadedParserWrapper m_parser = null;
    if (opts.nThreads > 1){
	  	System.out.println("Parsing with "+opts.nThreads+" threads in parallel.");
	  	m_parser = new MultiThreadedParserWrapper(parser, opts.nThreads);
		}
 */
    
    try{
    	BufferedReader inputData = (opts.inputFile==null) ? new BufferedReader(new InputStreamReader(System.in)) : new BufferedReader(new InputStreamReader(new FileInputStream(opts.inputFile), "UTF-8"));
    	PrintWriter outputData = (opts.outputFile==null) ? new PrintWriter(new OutputStreamWriter(System.out)) : new PrintWriter(new OutputStreamWriter(new FileOutputStream(opts.outputFile), "UTF-8"), true);
    	PTBLineLexer tokenizer = null;
    	if (opts.tokenize) tokenizer = new PTBLineLexer();

    	String line = "";
    	int scounter = 0;
    	int lcounter = 0;
    	
    	while((line=inputData.readLine()) != null){
      	List<String> sentence = null;
      	List<String> posTags = null;
      	lcounter += 1;
  
    		if (opts.goldPOS){
		      
    			sentence = new ArrayList<String>();
    			posTags = new ArrayList<String>();
  				List<String> tmp = Arrays.asList(line.split("\t"));
                            
  				if (tmp.size()==0) {continue;}
  				
  				scounter  = scounter+ 1;
  				lcounter += 1;
  				if (tmp.size()==1){
  					System.err.println("Line " + lcounter + ", sentence #" + scounter +": less than two columns." );
  					System.exit(1);}
  				
  				
  				sentence.add(tmp.get(0).replace("(","[").replace(")","]"));
  				
				String tag  = transformTag(tmp.get(1), tmp.get(0));
                posTags.add(tag); 
                            
    			while(!(line=inputData.readLine()).equals("")){
    			    tmp = Arrays.asList(line.split("\t"));
    			    lcounter += 1;
    				if (tmp.size()==0) break;
    				
    				if (tmp.size()==1){
      					System.err.println("Line " + lcounter + ", sentence #" + scounter +": less than two columns." );
      					System.exit(1);}
    				sentence.add(tmp.get(0).replace("(","[").replace(")","]"));
			        tag  = transformTag(tmp.get(1), tmp.get(0));
                    posTags.add(tag); 
    			}
    			} else {
    			scounter += 1;
    			lcounter += 1;
	    		if (!opts.tokenize) sentence = Arrays.asList(line.split(" "));
	    		else sentence = tokenizer.tokenizeLine(line);
    		}
    		
    		// set maximum sentence length (in tokens); sentences longer than this
    		// will not be parsed, but simply copied to outdata:
			if (sentence.size() > opts.maxLength) {System.err.println("Line " + lcounter + ": Skipping sentence #" + scounter + " with "+sentence.size()+" words since it is too long (limit: " + opts.maxLength + ")");
			if (opts.outputXML) {
				outputData.write("<s>\n"+String.join("\n",sentence) + "\n</s>\n");
				}
			else {
				outputData.write(String.join(" ",sentence) + "\n");
				}
			   sentence = new ArrayList<String>();
			   continue;
			   } // felix


    			List<Tree<String>> parsedTrees = null;
    			
    	  		parsedTrees = new ArrayList<Tree<String>>();
    	
    	  		Tree<String> parsedTree = parser.getBestConstrainedParse(sentence,posTags,null);
    	  		if (opts.goldPOS && parsedTree.getChildren().isEmpty()){ // parse error when using goldPOS, try without

    	  			String msgtext = null;
    	  			if (posTags != null) {
    	  				ArrayList<String> msg = new ArrayList<String>();
    	  				for (int w = 0; w < sentence.size(); w++){
    	  				msg.add(sentence.get(w)+"_"+posTags.get(w));}
    	  				msgtext = "Line " + lcounter + ": Ignoring POS tags in sentence #" + scounter + ": " + String.join(" ", msg);
    	  				}
    	  			else{
    	  				msgtext = "NO PARSE: " + String.join(" ", sentence) + "\n";
    	  				}
				    System.err.println(msgtext);
  	    			parsedTree = parser.getBestConstrainedParse(sentence,null,null);
  	    		}

    	  		parsedTrees.add(parsedTree);
    			
    			if(opts.outputXML){outputTreesXML(parsedTrees, outputData, parser, opts, sentence);}
    			else{outputTrees(parsedTrees, outputData, parser, opts, sentence);}
    			if (opts.render)		writeTreeToImage(parsedTrees.get(0),line.replaceAll("[^a-zA-Z]", "")+".png");
    		
    	}

  		outputData.flush();
  		outputData.close();
    } catch (Exception ex) {
      ex.printStackTrace();
    }
    
    System.exit(0);
  }



  /**
   * Add current sentence as an argument to outputTrees;
   * when there is no parse, output the unparsed sentence instead of "(())"
   * 
   * @param parseTrees
   * @param outputData
   * @param parser
   * @param opts
   * @param sentence
   */
 	private static void outputTrees(List<Tree<String>> parseTrees, PrintWriter outputData, 
			CoarseToFineMaxRuleParser parser, edu.berkeley.nlp.PCFGLA.BerkeleyParser.Options opts, List<String> sentence) {
		for (Tree<String> parsedTree : parseTrees){

			parsedTree = TreeAnnotations.unAnnotateTree(parsedTree);
			if (opts.confidence & !opts.outputXML) {
				double treeLL = (parsedTree.getChildren().isEmpty()) ? Double.NEGATIVE_INFINITY : parser.getLogLikelihood(parsedTree);
				outputData.write(treeLL+"\t");
			}

			if (!parsedTree.getChildren().isEmpty()) { 
	       			if (true) outputData.write(parsedTree.getChildren().get(0)+"\n");
	    } else {
	    	outputData.write(String.join(" ", sentence) + "\n");
	    }
		}
	}

 	//  
 		
 	/**
 	 * Generate XML-like output, one token per line. 
 	 * Labels that should be turned into XML tags
 	 * must be listed in edu.berkeley.nlp.ling.TopoLabels
 	 * Any label not listed there will be omitted from the output.
 	 * 
 	 * @param parseTrees
 	 * @param outputData
 	 * @param parser
 	 * @param opts
 	 * @param sentence
 	 */
 	private static void outputTreesXML(List<Tree<String>> parseTrees, PrintWriter outputData, 
			CoarseToFineMaxRuleParser parser, edu.berkeley.nlp.PCFGLA.BerkeleyParser.Options opts, List<String> sentence) {
		for (Tree<String> parsedTree : parseTrees){
			
			parsedTree = TreeAnnotations.unAnnotateTree(parsedTree);
			
			if (!parsedTree.getChildren().isEmpty()) { 
	       		outputData.write("<s>\n" + parsedTree.getChildren().get(0).otpl() + "\n</s>\n");	       			
	    } else {
	   
	    	outputData.write("<s>\n" + String.join("\n", sentence) + "\n</s>\n");
	    }
		}
	}
 	
 	/**
 	 * Transform some POS tags from standard STTS
 	 * to a version the parser knows about:
 	 * @author Felix Bildhauer
 	 * @param originalTag
 	 * @param token
 	 * @return
 	 */
	
	private static String transformTag(String originalTag, String token){
	String newTag = originalTag;
	if (token.toLowerCase().matches("(?:alle|viele|beid).*")){
	  newTag = newTag.replace("PIAT","PIDAT");
	}
	else{
	  if (token.toLowerCase().equals("als")){
	    newTag = newTag.replace("KON","KOUS");
	  } 
	   else{
	     newTag = newTag.replace("$(", "$[").replace("PAV","PROP");
	   }	
	}
	return newTag;
	}

	
	

	public static void writeTreeToImage(Tree<String> tree, String fileName) throws IOException{
  	tjp.setTree(tree);
    
    BufferedImage bi =new BufferedImage(tjp.width(),tjp.height(),BufferedImage.TYPE_INT_ARGB);
    int t=tjp.height();
    Graphics2D g2 = bi.createGraphics();
    
    
    g2.setComposite(AlphaComposite.getInstance(AlphaComposite.CLEAR, 1.0f));
    Rectangle2D.Double rect = new Rectangle2D.Double(0,0,tjp.width(),tjp.height()); 
    g2.fill(rect);
    
    g2.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 1.0f));
    
    tjp.paintComponent(g2); //paint the graphic to the offscreen image
    g2.dispose();
    
    ImageIO.write(bi,"png",new File(fileName)); //save as png format DONE!
  }

}

