class LazyOperation():
    '''
    A class that supports TimeSeries class to compute in lazy mode.

    Attribute
    ---------
    function : function
        function that this LazyOperation() instance actually operates as
    args : int or float
        arguments for LazyOperation() function
    kwargs : int or float
        arguemtns for LazyOperation() function
    '''
    def __init__(self, function, *args, **kwargs):
        '''
        This initializes a LazyOperation instance with
        inputs of a function, and other arguments.

        Parameters
        ----------
        function : function
            function that this LazyOperation() instance actually operates as

        Examples
        --------
        >>> @lazy
            def lazy_add(a,b):
                return a+b
        >>> isinstance( lazy_add(1,2), LazyOperation )
        True
        '''
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def eval(self):
        '''
        Evaluates the actual value of LazyOperation() instances.

        Returns
        -------
        int
            value

        Examples
        --------
        >>> @lazy
            def lazy_add(a,b):
                return a+b
        >>> lazy_add(2,4).eval()
        6
        '''
        temp_list = []
        for arg in self.args[0]:
            if isinstance(arg , LazyOperation):
                temp_list.append(arg .eval())
            else:
                temp_list.append(arg)

        return self.function(*temp_list)

def lazy(old_function):
    def wrapper(*args, **kwargs):
        return LazyOperation(old_function, args, kwargs)
    return wrapper
