/**
 * 
 */
package edu.berkeley.nlp.PCFGLA;

import java.util.List;

import edu.berkeley.nlp.PCFGLA.smoothing.Smoother;
import edu.berkeley.nlp.ling.StateSet;
import edu.berkeley.nlp.ling.Tree;

/**
 * @author petrov
 *
 */
public interface Lexicon {
	public void optimize();
	public double[] score(String word, short tag, int loc, boolean noSmoothing, boolean isSignature);
	public double[] score(StateSet stateSet, short tag, boolean noSmoothing, boolean isSignature);
	public double[] scoreWord(StateSet stateSet, int tag);
	public double[] scoreSignature(StateSet stateSet, int tag);
	public String getSignature(String word, int loc);
	public void logarithmMode();
	public boolean isLogarithmMode();
	public void trainTree(Tree<StateSet> trainTree, double randomness, Lexicon oldLexicon, boolean secondHalf, boolean noSmoothing); 
	public void setSmoother(Smoother smoother);
	public Lexicon splitAllStates(int[] counts, boolean moreSubstatesThanCounts, int mode);
	public void mergeStates(boolean[][][] mergeThesePairs, double[][] mergeWeights);
	public Smoother getSmoother();
	public double[] getSmoothingParams();
	public Lexicon projectLexicon(double[] condProbs, int[][] mapping, int[][] toSubstateMapping);
	public Lexicon copyLexicon();
	public void removeUnlikelyTags(double threshold, double exponent);
	public double getPruningThreshold();

	public void explicitlyComputeScores(int finalLevel);
}
