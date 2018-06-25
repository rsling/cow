package edu.berkeley.nlp.classify;

/**
 * LabeledInstances are input instances along with a label.
 * 
 * @author Dan Klein
 */
public class LabeledInstance<I,L> {
  I instance;
  L label;
  double[] weights;

  public I getInput() {
    return instance;
  }

  public L getLabel() {
    return label;
  }

  public double[] getWeights() {
    return weights;
  }

  public int getNumSubStates() {
    return weights.length;
  }

  public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof LabeledInstance)) return false;

    final LabeledInstance labeledInstance = (LabeledInstance) o;

    if (instance != null ? !instance.equals(labeledInstance.instance) : labeledInstance.instance != null) return false;
    if (label != null ? !label.equals(labeledInstance.label) : labeledInstance.label != null) return false;

    return true;
  }

  public int hashCode() {
    int result;
    result = (instance != null ? instance.hashCode() : 0);
    result = 29 * result + (label != null ? label.hashCode() : 0);
    return result;
  }

  public LabeledInstance(L label, I instance) {
    this.label = label;
    this.instance = instance;
    weights = new double[1];
    weights[0] = 1;
  }

  public LabeledInstance(L label, I instance, double[] weights) {
    this.label = label;
    this.instance = instance;
    this.weights = weights;
  }
}
