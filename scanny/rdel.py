
from scripty import *


with store.begin(write=True):
    for resource in Resource.iter():
        print resource
    print

    for resource in Resource.iter():
        print resource
        resource.delete()

