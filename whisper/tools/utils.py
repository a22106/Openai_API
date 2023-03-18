import time
class utils:
  @staticmethod
  def ttime(func):
      def wrapper(*args, **kwargs):
          start_time = time.time()
          result = func(*args, **kwargs)
          end_time = time.time()
          print(f"Function {func.__name__} took {(end_time - start_time):.2f} seconds to execute.")
          return result
      return wrapper