package edu.berkeley.nlp.util;

import java.io.Serializable;


/**
 * A generic-typed pair of objects.
 * @author Dan Klein
 */
public class Pair<F,S> implements Serializable{
	private static final long serialVersionUID = 1L;
	F first;
  S second;

  public F getFirst() {
    return first;
  }

  public S getSecond() {
    return second;
  }

  public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof Pair)) return false;

    final Pair pair = (Pair) o;

    if (first != null ? !first.equals(pair.first) : pair.first != null) return false;
    if (second != null ? !second.equals(pair.second) : pair.second != null) return false;

    return true;
  }

  public int hashCode() {
    int result;
    result = (first != null ? first.hashCode() : 0);
    result = 29 * result + (second != null ? second.hashCode() : 0);
    return result;
  }

  public String toString() {
    return "(" + getFirst() + ", " + getSecond() + ")";
  }

  public Pair(F first, S second) {
    this.first = first;
    this.second = second;
  }

	public void setFirst(F first) {
		this.first = first;
	}

	public void setSecond(S second) {
		this.second = second;
	}
	
  /**
   * Convenience method for construction of a <code>Pair</code> with
   * the type inference on the arguments. So for instance we can type  
   *     <code>Pair<Tree<String>, Double> treeDoublePair = makePair(tree, count);</code>
   *  instead of,
   *   	 <code>Pair<Tree<String>, Double> treeDoublePair = new Pair<Tree<String>, Double>(tree, count);</code>
   * @author Aria Haghighi
   * @param <F>
   * @param <S>
   * @param f
   * @param s
   * @return <code>Pair<F,S></code> with the arguments <code>f</code>  and <code>s</code>
   */
  public static <F,S> Pair<F,S> makePair(F f, S s) {
	  return new Pair<F,S>(f,s);
  }
}
