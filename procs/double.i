%module darray
%inline %{
double *new_darray(int size) {
return (double *) malloc(size*sizeof(double));
}
double darray_get(double *a, int index) {
return a[index];
}
void darray_set(double *a, int index, double value) {
a[index] = value;
}
%}
%rename(delete_darray) free(void *);