package edu.berkeley.nlp.math;

import java.util.LinkedList;

/**
 * @author Dan Klein
 */
public class LBFGSMinimizer implements GradientMinimizer {
  double EPS = 1e-10;
  int maxIterations = 10; //was 20
  int maxHistorySize = 5;
  LinkedList<double[]> inputDifferenceVectorList = new LinkedList<double[]>();
  LinkedList<double[]> derivativeDifferenceVectorList = new LinkedList<double[]>();
  IterationCallbackFunction iterCallbackFunction = null;
  int minIterations = 1;
  double initialStepSizeMultiplier = 0.01;
  double stepSizeMultiplier = 0.1;//was 0.5
  
  public static interface IterationCallbackFunction {
    public void iterationDone(double[] curGuess,int iter);
  }
  
  public void setMinIteratons(int minIterations) {
    this.minIterations = minIterations;    
  }

  public void setInitialStepSizeMultiplier(double initialStepSizeMultiplier) {
	this.initialStepSizeMultiplier = initialStepSizeMultiplier;  
  }
  
  public void setStepSizeMultiplier(double stepSizeMultiplier) {
	  this.stepSizeMultiplier = stepSizeMultiplier;
  }
  
  public double[] getSearchDirection(int dimension, double[] derivative){
    double[] initialInverseHessianDiagonal = getInitialInverseHessianDiagonal(dimension);
    double[] direction = implicitMultiply(initialInverseHessianDiagonal, derivative);
    return direction;
  }
  
  public double[] minimize(DifferentiableFunction function, double[] initial, double tolerance) {
    BacktrackingLineSearcher lineSearcher = new BacktrackingLineSearcher();
    double[] guess = DoubleArrays.clone(initial);
    for (int iteration = 0; iteration < maxIterations; iteration++) {
      double value = function.valueAt(guess);
      double[] derivative = function.derivativeAt(guess);
      double[] direction = getSearchDirection(function.dimension(), derivative);
      //      System.out.println(" Derivative is: "+DoubleArrays.toString(derivative, 100));
//      DoubleArrays.assign(direction, derivative);
      DoubleArrays.scale(direction, -1.0);
//      System.out.println(" Looking in direction: "+DoubleArrays.toString(direction, 100));
      if (iteration == 0)
        lineSearcher.stepSizeMultiplier = initialStepSizeMultiplier;
      else
        lineSearcher.stepSizeMultiplier = stepSizeMultiplier;
      double[] nextGuess = lineSearcher.minimize(function, guess, direction, false);
      double nextValue = function.valueAt(nextGuess);
      double[] nextDerivative = function.derivativeAt(nextGuess);
      
      System.out.printf("Iteration %d ended with value %.6f\n", iteration, nextValue);
      
      if (iteration >= minIterations && converged(value, nextValue, tolerance))
        return nextGuess;
      
      updateHistories(guess, nextGuess, derivative, nextDerivative);;
      guess = nextGuess;
      value = nextValue;
      derivative = nextDerivative;
      if (iterCallbackFunction != null) {
        iterCallbackFunction.iterationDone(guess,iteration);
      }
    }
    //System.err.println("LBFGSMinimizer.minimize: Exceeded maxIterations without converging.");
    return guess;
  }

  protected boolean converged(double value, double nextValue, double tolerance) {
    if (value == nextValue)
      return true;
    double valueChange = SloppyMath.abs(nextValue - value);
    double valueAverage = SloppyMath.abs(nextValue + value + EPS) / 2.0;
    if (valueChange / valueAverage < tolerance)
      return true;
    return false;
  }

  protected void updateHistories(double[] guess, double[] nextGuess, double[] derivative, double[] nextDerivative) {
    double[] guessChange = DoubleArrays.addMultiples(nextGuess, 1.0, guess, -1.0);
    double[] derivativeChange = DoubleArrays.addMultiples(nextDerivative, 1.0, derivative,  -1.0);
    pushOntoList(guessChange, inputDifferenceVectorList);
    pushOntoList(derivativeChange,  derivativeDifferenceVectorList);
  }

  protected void pushOntoList(double[] vector, LinkedList<double[]> vectorList) {
    vectorList.addFirst(vector);
    if (vectorList.size() > maxHistorySize)
      vectorList.removeLast();
  }

  protected int historySize() {
    return inputDifferenceVectorList.size();
  }

  public void setMaxHistorySize(int maxHistorySize) {
	 this.maxHistorySize = maxHistorySize;
  }
  
  protected double[] getInputDifference(int num) {
    // 0 is previous, 1 is the one before that
    return inputDifferenceVectorList.get(num);
  }
  
  protected double[] getDerivativeDifference(int num) {
    return derivativeDifferenceVectorList.get(num);
  }

  protected double[] getLastDerivativeDifference() {
    return derivativeDifferenceVectorList.getFirst();
  }

  protected double[] getLastInputDifference() {
    return inputDifferenceVectorList.getFirst();
  }


  protected double[] implicitMultiply(double[] initialInverseHessianDiagonal, double[] derivative) {
    double[] rho = new double[historySize()];
    double[] alpha = new double[historySize()];
    double[] right = DoubleArrays.clone(derivative);
    // loop last backward
    for (int i = historySize()-1; i >= 0; i--) {
      double[] inputDifference = getInputDifference(i);
      double[] derivativeDifference = getDerivativeDifference(i);
      rho[i] = DoubleArrays.innerProduct(inputDifference, derivativeDifference);
      if (rho[i] == 0.0)
        throw new RuntimeException("LBFGSMinimizer.implicitMultiply: Curvature problem.");
      alpha[i] = DoubleArrays.innerProduct(inputDifference, right) / rho[i];
      right = DoubleArrays.addMultiples(right, 1.0, derivativeDifference, -1.0*alpha[i]);
    }
    double[] left = DoubleArrays.pointwiseMultiply(initialInverseHessianDiagonal, right);
    for (int i = 0; i < historySize(); i++) {
      double[] inputDifference = getInputDifference(i);
      double[] derivativeDifference = getDerivativeDifference(i);
      double beta = DoubleArrays.innerProduct(derivativeDifference, left) / rho[i];
      left = DoubleArrays.addMultiples(left, 1.0, inputDifference, alpha[i] - beta);
    }
    return left;
  }

  protected double[] getInitialInverseHessianDiagonal(int dimension) {
    double scale = 1.0;
    if (derivativeDifferenceVectorList.size() >= 1) {
      double[] lastDerivativeDifference = getLastDerivativeDifference();
      double[] lastInputDifference = getLastInputDifference();
      double num = DoubleArrays.innerProduct(lastDerivativeDifference, lastInputDifference);
      double den = DoubleArrays.innerProduct(lastDerivativeDifference, lastDerivativeDifference);
      scale = num / den;
    }
    return DoubleArrays.constantArray(scale, dimension);
  }

  public void setIterationCallbackFunction(IterationCallbackFunction callbackFunction) {
    this.iterCallbackFunction = callbackFunction;
  }
  
  public LBFGSMinimizer() {
  }

  public LBFGSMinimizer(int maxIterations) {
    this.maxIterations = maxIterations;
  }

}
