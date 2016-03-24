class LazyOperation():
    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs
        
    def eval(self):
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