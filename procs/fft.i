/* File: example.i */
%module fft

%{
#include "fft.h"
%}

%include fft.h
void four1(double data[], int nn, int isign);
