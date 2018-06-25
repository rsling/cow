/**
 * 
 */
package edu.berkeley.nlp.classify;

import edu.berkeley.nlp.math.DifferentiableFunction;
import edu.berkeley.nlp.util.Pair;

/**
 * @author petrov
 *
 */
public interface ObjectiveFunction extends DifferentiableFunction {
	<F,L> double[] getLogProbabilities(EncodedDatum datum, double[] weights, Encoding<F, L> encoding, IndexLinearizer indexLinearizer);
	//Pair<Double, double[]> calculate();
	public void shutdown();
	  

}
