from abc import ABC, abstractmethod

class CloudStorage(ABC) :
  ''' This is an abstract base class for cloud storage.
      It defines a generic interface to implement
  '''

  def __init__(self):
    print('init stub')


  @abstractmethod
  def upload_file(self, filename: str, bucket: str, key: str, public: bool = False):
    pass

