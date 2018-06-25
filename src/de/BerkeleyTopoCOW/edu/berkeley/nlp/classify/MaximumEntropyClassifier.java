package edu.berkeley.nlp.classify;

import edu.berkeley.nlp.math.GradientMinimizer;
import edu.berkeley.nlp.math.LBFGSMinimizer;
import edu.berkeley.nlp.math.DifferentiableFunction;
import edu.berkeley.nlp.math.DoubleArrays;
import edu.berkeley.nlp.math.SloppyMath;
import edu.berkeley.nlp.util.SubIndexer;
import edu.berkeley.nlp.util.Indexer;
import edu.berkeley.nlp.util.Pair;
import edu.berkeley.nlp.util.Counter;
import edu.berkeley.nlp.util.CounterMap;

import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

/**
 * Maximum entropy classifier. It was modified to allow training examples to be "soft": the label is
 * known but with a distribution over the sublabel.
 * No longer implements ProbabilisticClassifier<I, L>
 * <p/>
 * java edu.berkeley.nlp.assignments.MaximumEntropyClassifier
 * <p/>
 * This will run a toy test classification.
 *
 * 
 * @author Dan Klein
 * @author Romain Thibaux
 */
public class MaximumEntropyClassifier <I,F,L> {

  /**
   * Factory for training MaximumEntropyClassifiers.
   * No longer implements ProbabilisticClassifierFactory<I,L> 
   */
  public static class Factory<I,F,L> {

    double sigma;
    int iterations;
    FeatureExtractor<I, F> featureExtractor;

    public MaximumEntropyClassifier<I,F,L> trainClassifier(List<LabeledInstance<I, L>> trainingData) {
      // build data encodings so the inner loops can be efficient
      Encoding<F, L> encoding = buildEncoding(trainingData);
      IndexLinearizer indexLinearizer = buildIndexLinearizer(encoding);
      double[] initialWeights = buildInitialWeights(indexLinearizer);
      EncodedDatum[] data = encodeData(trainingData, encoding);
      // build a minimizer object
      GradientMinimizer minimizer = new LBFGSMinimizer(iterations);
      // build the objective function for this data
      ObjectiveFunction objective = new ProperNameObjectiveFunction<F, L>(encoding, data, indexLinearizer, sigma);
      //testDerivatives(objective);
      // learn our voting weights
      double[] weights = minimizer.minimize(objective, initialWeights, 1e-4);
      // build a classifer using these weights (and the data encodings)
      return new MaximumEntropyClassifier<I,F,L>(weights, encoding, indexLinearizer, featureExtractor,objective);
    }
    
    private void testDerivatives(DifferentiableFunction objective) {
      double[] x = DoubleArrays.constantArray(0.0, objective.dimension());
      double[] deriv1 = objective.derivativeAt(x);
      double[] deriv2 = DoubleArrays.constantArray(0.0, objective.dimension());
      double f = objective.valueAt(x);
      double epsilon = 1e-4;
      for (int i = 0; i < x.length; ++i) {
        double[] y = DoubleArrays.clone(x);
        y[i] += epsilon; 
        double fi = objective.valueAt(y);
        deriv2[i] = (fi-f)/epsilon;
        System.out.println(deriv1[i] + " " + deriv2[i] + "(" + fi + ", " + f + ")");
      }
    }

    private double[] buildInitialWeights(IndexLinearizer indexLinearizer) {
      return DoubleArrays.constantArray(0.0, indexLinearizer.getNumLinearIndexes());
    }

    private IndexLinearizer buildIndexLinearizer(Encoding<F, L> encoding) {
      return new IndexLinearizer(encoding.getNumFeatures(), encoding.getNumSubLabels());
    }

    private Encoding<F, L> buildEncoding(List<LabeledInstance<I,L>> data) {
      Indexer<F> featureIndexer = new Indexer<F>();
      SubIndexer<L> labelIndexer = new SubIndexer<L>();
      for (LabeledInstance<I,L> labeledInstance : data) {
        L label = labeledInstance.getLabel();
        Counter<F> features = featureExtractor.extractFeatures(labeledInstance.getInput());
        //LabeledFeatureVector<F,L> labeledDatum = new BasicLabeledFeatureVector<F,L>(label, features);
        //labelIndexer.add(labeledDatum.getLabel());
        labelIndexer.add(label, labeledInstance.getNumSubStates());
        //for (F feature : labeledDatum.getFeatures().keySet()) {
        for (F feature : features.keySet()) {
          featureIndexer.add(feature);
        }
      }
      return new Encoding<F, L>(featureIndexer, labelIndexer);
    }

    private EncodedDatum[] encodeData(List<LabeledInstance<I,L>> data, Encoding<F, L> encoding) {
      EncodedDatum[] encodedData = new EncodedDatum[data.size()];
      for (int i = 0; i < data.size(); i++) {
        LabeledInstance<I,L> labeledInstance = data.get(i);
        L label = labeledInstance.getLabel();
        double[] weights = labeledInstance.getWeights();
        Counter<F> features = featureExtractor.extractFeatures(labeledInstance.getInput());
        encodedData[i] = EncodedDatum.encodeLabeledDatum(encoding, features, label, weights);
      }
      return encodedData;
    }

    /**
     * Sigma controls the variance on the prior / penalty term.  1.0 is a reasonable value for large problems, bigger
     * sigma means LESS smoothing. Zero sigma is a special indicator that no smoothing is to be done.
     * <p/>
     * Iterations determines the maximum number of iterations the optimization code can take before stopping.
     */
    public Factory(double sigma, int iterations, FeatureExtractor<I,F> featureExtractor) {
      this.sigma = sigma;
      this.iterations = iterations;
      this.featureExtractor = featureExtractor;
    }
  }


  


 

  private double[] weights;
  private Encoding<F,L> encoding;
  private IndexLinearizer indexLinearizer;
  private FeatureExtractor<I,F> featureExtractor;
  private static double numLogs = 0.0;
  private static double numLogsSaved = 0.0;
  private ObjectiveFunction objective;

  public static void displaySavings() {
    System.out.println("Saved " + (100.0*numLogsSaved/numLogs) + "% calls to log()");
  }
  
  

  // TODO: change these two functions and its return type to acccount for substates:
  public CounterMap<L,Integer> getProbabilities(I input) {
    Counter<F> features = featureExtractor.extractFeatures(input);
    EncodedDatum encodedDatum = EncodedDatum.encodeDatum(encoding, features);
    double[] logProbabilities = objective.getLogProbabilities(encodedDatum, weights, encoding, indexLinearizer);
    return logProbabilityArrayToProbabilityCounter(logProbabilities);
  }

  private CounterMap<L, Integer> logProbabilityArrayToProbabilityCounter(double[] logProbabilities) {
    CounterMap<L, Integer> probabilityCounter = new CounterMap<L, Integer>();
    for (int C = 0; C < encoding.getNumLabels(); C++ ) {
      L label = encoding.getLabel(C);
      int subStateBegin = encoding.getLabelSubindexBegin(C);
      int subStateEnd = encoding.getLabelSubindexEnd(C);
      for (int c = subStateBegin; c < subStateEnd; c++) {
        double logProbability = logProbabilities[c];
        double probability = Math.exp(logProbability);
        probabilityCounter.setCount(label, c - subStateBegin, probability);
      }
    }
    /*
    for (int labelIndex = 0; labelIndex < logProbabilities.length; labelIndex++) {
      double logProbability = logProbabilities[labelIndex];
      double probability = Math.exp(logProbability);
      L label = encoding.getLabel(labelIndex);
      probabilityCounter.setCount(label, probability);
    }*/
    return probabilityCounter;
  }

  public Pair<L, Integer> getLabel(I input) {
    return getProbabilities(input).argMax();
  }

  public MaximumEntropyClassifier(double[] weights, Encoding<F, L> encoding, IndexLinearizer indexLinearizer, FeatureExtractor<I,F> featureExtractor,
  		ObjectiveFunction objective) {
    this.weights = weights;
    this.encoding = encoding;
    this.indexLinearizer = indexLinearizer;
    this.featureExtractor = featureExtractor;
    this.objective = objective;
  }

  public static void main(String[] args) {
    // create datums
    int k = 2;
    double[] dummyWeights = DoubleArrays.constantArray(1.0/(double) k, k);
    LabeledInstance<String[], String> datum1 = new LabeledInstance<String[], String>("cat", new String[]{"fuzzy", "claws", "small"});
    LabeledInstance<String[], String> datum2 = new LabeledInstance<String[], String>("bear", new String[]{"fuzzy", "claws", "big"});//, dummyWeights);
    LabeledInstance<String[], String> datum3 = new LabeledInstance<String[], String>("cat", new String[]{"claws", "medium"});
    LabeledInstance<String[], String> datum4 = new LabeledInstance<String[], String>("cat", new String[]{"claws", "small"});

    // create training set
    List<LabeledInstance<String[], String>> trainingData = new ArrayList<LabeledInstance<String[], String>>();
    trainingData.add(datum1);
    trainingData.add(datum2);
    trainingData.add(datum3);

    // create test set
    List<LabeledInstance<String[], String>> testData = new ArrayList<LabeledInstance<String[], String>>();
    testData.add(datum4);

    // build classifier
    FeatureExtractor<String[], String> featureExtractor = new FeatureExtractor<String[], String>() {
      public Counter<String> extractFeatures(String[] featureArray) {
        return new Counter<String>(Arrays.asList(featureArray));
      }
    };
    MaximumEntropyClassifier.Factory<String[], String, String> maximumEntropyClassifierFactory = new MaximumEntropyClassifier.Factory<String[], String, String>(1.0, 20, featureExtractor);
    MaximumEntropyClassifier<String[], String, String> maximumEntropyClassifier = maximumEntropyClassifierFactory.trainClassifier(trainingData);
    System.out.println("Probabilities on test instance: " + maximumEntropyClassifier.getProbabilities(datum4.getInput()));
  }
}













