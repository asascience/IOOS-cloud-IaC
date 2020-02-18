from abc import ABC, abstractmethod

class StorageService(ABC) :
  ''' This is an abstract base class for cloud storage.
      It defines a generic interface to implement
  '''

  def __init__(self):
    print('init stub')


  @abstractmethod
  def upload_file(self, filename: str, bucket: str, key: str, public: bool = False):
    pass

if __name__ == '__main__':
  pass
