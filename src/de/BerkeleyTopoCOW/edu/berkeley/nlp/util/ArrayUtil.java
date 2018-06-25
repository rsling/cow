package edu.berkeley.nlp.util;
import java.util.Arrays;

import edu.berkeley.nlp.math.ArrayMath;

public class ArrayUtil {

  public static boolean[][] clone(boolean[][] a) {
  	boolean[][] res = new boolean[a.length][];
    for (int i=0; i<a.length; i++){
    	if (a[i]!=null) res[i] = a[i].clone();
    }
    return res;
  }

  public static boolean[][][] clone(boolean[][][] a) {
  	boolean[][][] res = new boolean[a.length][][];
    for (int i=0; i<a.length; i++){
    	if (a[i]!=null) res[i] = clone(a[i]);
    }
    return res;
  }
	
  public static boolean[][][][] clone(boolean[][][][] a) {
  	boolean[][][][] res = new boolean[a.length][][][];
    for (int i=0; i<a.length; i++){
    	res[i] = clone(a[i]);
    }
    return res;
  }
  
  public static int[][] clone(int[][] a) {
  	int[][] res = new int[a.length][];
    for (int i=0; i<a.length; i++){
    	if (a[i]!=null) res[i] = a[i].clone();
    }
    return res;
  }

  public static double[][] clone(double[][] a) {
  	double[][] res = new double[a.length][];
    for (int i=0; i<a.length; i++){
    	if (a[i]!=null) res[i] = a[i].clone();
    }
    return res;
  }

  public static double[][][] clone(double[][][] a) {
  	double[][][] res = new double[a.length][][];
    for (int i=0; i<a.length; i++){
    	if (a[i]!=null) res[i] = clone(a[i]);
    }
    return res;
  }
	
  public static double[][][][] clone(double[][][][] a) {
  	double[][][][] res = new double[a.length][][][];
    for (int i=0; i<a.length; i++){
    	res[i] = clone(a[i]);
    }
    return res;
  }
	
	public static void fill(float[][] a, float val) {
    for (int i=0; i<a.length; i++){
    	Arrays.fill(a[i],val);
    }
  }
  
  public static void fill(float[][][] a, float val) {
    for (int i=0; i<a.length; i++){
    	fill(a[i],val);
    }
  }

  public static void fill(int[][] a, int val) {
    for (int i=0; i<a.length; i++){
    	Arrays.fill(a[i],val);
    }
  }
  
  public static void fill(int[][][] a, int val) {
    for (int i=0; i<a.length; i++){
    	fill(a[i],val);
    }
  }

  
  public static void fill(double[][] a, double val) {
    for (int i=0; i<a.length; i++){
    	Arrays.fill(a[i],val);
    }
  }
  
  public static void fill(double[][][] a, double val) {
    for (int i=0; i<a.length; i++){
    	fill(a[i],val);
    }
  }

  public static void fill(double[][][] a, int until, double val) {
    for (int i=0; i<until; i++){
    	fill(a[i],val);
    }
  }
  
  public static void fill(int[][][] a, int until, int val) {
    for (int i=0; i<until; i++){
    	fill(a[i],val);
    }
  }

  public static void fill(boolean[][] a, boolean val) {
    for (int i=0; i<a.length; i++){
    	Arrays.fill(a[i],val);
    }
  }
  
  public static String toString(float[][] a) {
    String s = "[";
  	for (int i=0; i<a.length; i++){
    	s = s.concat(Arrays.toString(a[i])+", ");
    }
  	return s + "]";
  }
  
  public static String toString(float[][][] a) {
    String s = "[";
    for (int i=0; i<a.length; i++){
    	s = s.concat(toString(a[i])+", ");
    }
    return s + "]";
  }

  public static String toString(double[][] a) {
    String s = "[";
  	for (int i=0; i<a.length; i++){
    	s = s.concat(Arrays.toString(a[i])+", ");
    }
  	return s + "]";
  }
  
  public static String toString(double[][][] a) {
    String s = "[";
    for (int i=0; i<a.length; i++){
    	s = s.concat(toString(a[i])+", ");
    }
    return s + "]";
  }

  public static String toString(boolean[][] a) {
    String s = "[";
  	for (int i=0; i<a.length; i++){
    	s = s.concat(Arrays.toString(a[i])+", ");
    }
  	return s + "]";
  }
  
  public static double[][] copyArray(double[][] a) {
    if (a==null) return null;
  	double[][] res = new double[a.length][];
    for (int i=0; i<a.length; i++){
    	if (a[i] == null) continue;
    	res[i] = a[i].clone();
    }
    return res;
  }
  public static void copyArray(double[][] a, double[][] res) {
    
    for (int i=0; i<a.length; i++){
    	if (a[i] == null) continue;
    	for (int j = 0; j < a[i].length; ++j)
    	{
    	res[i][j] = a[i][j];
    	}
    }
   
  }

  public static double[][][] copyArray(double[][][] a) {
    if (a==null) return null;
    double[][][] res = new double[a.length][][];
    for (int i=0; i<a.length; i++){
    	res[i] = copyArray(a[i]);
    }
    return res;
  }

	public static void multiplyInPlace(double[][][] array, double d) {
		for (int i=0; i<array.length; i++){
			multiplyInPlace(array[i], d);
		}
	}

	public static void multiplyInPlace(double[][] array, double d) {
		for (int i=0; i<array.length; i++){
			multiplyInPlace(array[i], d);
		}
	}

	public static void multiplyInPlace(double[] array, double d) {
		if (array==null) return;
		for (int i=0; i<array.length; i++){
			array[i] *= d;
		}
	}

	public static void addInPlace(double[][][] a, double[][][] b) {
		if (a == null || b == null)
			return;
		if (a.length != b.length)
			return;
		for (int i = 0; i < a.length; ++i) {
	
			addInPlace(a[i], b[i]);
	
		}
	}

	public static void addInPlace(double[][][][] a, double[][][][] b) {
		if (a == null || b == null)
			return;
		if (a.length != b.length)
			return;
		for (int i = 0; i < a.length; ++i) {
	
			addInPlace(a[i], b[i]);
	
		}
	}

	public static void addInPlace(double[][] a, double[][] b) {
		if (a == null || b == null)
			return;
		if (a.length != b.length)
			return;
		for (int i = 0; i < a.length; ++i) {
			if (a[i] == null || b[i] == null)
				continue;
			ArrayMath.addInPlace(a[i], b[i]);
	
		}
	}
	
	public static void subtractInPlace(double[][] a, double[][] b) {
		if (a == null || b == null)
			return;
		if (a.length != b.length)
			return;
		for (int i = 0; i < a.length; ++i) {
			if (a[i] == null || b[i] == null)
				continue;
			ArrayMath.subtractInPlace(a[i], b[i]);
	
		}
	}

	public static double product(double[] a) {
		double retVal = 1.0;
		boolean hadZero = false;
		for (double d : a) {
			if (d != 0)
				retVal *= d;
			if (d == 0)
				hadZero = true;
		}
		// if (hadZero) System.out.println("variance droppped to zero");
		return retVal;
	}

	public static double[] inverse(double[] a) {
	
		double[] retVal = new double[a.length];
		for (int i = 0; i < a.length; ++i) {
	
			retVal[i] = (a[i] == 0.0) ? 0 : // Double.POSITIVE_INFINITY :
					1.0 / a[i];
		}
	
		return retVal;
	}

	static double[][] outerProduct(double[] a, double[] b) {
		if (a.length != b.length) {
			return null;
		}
		double[][] retVal = new double[a.length][a.length];
		for (int i = 0; i < a.length; ++i) {
			for (int j = 0; j < a.length; ++j) {
				retVal[i][j] = a[i] * b[j];
			}
		}
		return retVal;
	}

	/**
	 * @param sumSq
	 * @param d
	 * @return
	 */
	public static double[][] multiply(double[][] sumSq, double d) {
		double[][] retVal = new double[sumSq.length][];
		for (int i = 0; i < sumSq.length; ++i)
		{
			retVal[i] = new double[sumSq[i].length];
			retVal[i] = ArrayMath.multiply(sumSq[i],d);
		}
		return retVal;
	}
	
	public static String toString(double[] array)
	{
		if (array == null) return "[null]";
		StringBuffer s = new StringBuffer("");
		s.append("[");
		for (int i = 0; i < array.length; ++i)
		{
			if (i > 0) s.append(",");
			s.append(array[i]);
		}
		s.append("]");
		return s.toString();
	}
	
	
}
