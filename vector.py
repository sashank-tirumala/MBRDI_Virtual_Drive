import math

class Vector(object):
    def __init__(self,x,y,z):
        """ Create a vector, example: v = Vector(1,2) """
        self.x = x
        self.y = y
        self.z = z
        
    def norm(self):
        """ Returns the norm (length, magnitude) of the vector """
        return math.sqrt(self.x*self.x+self.y*self.y+self.z*self.z)
        
    def argument(self):
        """ Returns the argument of the vector, the angle anticlockwise from x."""
        arg_in_deg = 0
        if self.x == 0: arg_in_deg = 90
        if self.x> 0 and self.y > 0:
            arg_in_deg = math.degrees(math.atan((self.y/self.x)))
        if self.x>0 and self.y < 0:
            y = self.y*-1
            arg_in_deg = 360 - math.degrees(math.atan(y/self.x))
        if self.x<0 and self.y < 0:
            x = self.x*-1
            y = self.y*-1
            arg_in_deg = 180 + math.degrees(math.atan(y/x))
        if self.x<0 and self.y > 0:
            x = self.x*-1
            arg_in_deg = 180 - math.degrees(math.atan(self.y/x))
        return arg_in_deg

    def normalize(self):
        """ Returns a normalized unit vector """
        norm = self.norm()
        return Vector(self.x/norm,self.y/norm,self.z/norm)
    
    def rotate(self, theta):
        """ Rotate this vector about z axis
        """
        theta = math.radians(theta)
        dc, ds = math.cos(theta), math.sin(theta)
        x, y = dc*self.x - ds*self.y, ds*self.x + dc*self.y
        return Vector(x, y, self.z)
    
    def inner(self, other):
        """ Returns the dot product (inner product) of self and other vector
        """
        return self.x*other.x + self.y*other.y + self.z*other.z
    
    def __mul__(self, other):
        """ Returns the dot product of self and other if multiplied
            by another Vector.  If multiplied by an int or float,
            multiplies each component by other.
        """
        if type(other) == type(self):
            return self.inner(other)
        elif type(other) == type(1) or type(other) == type(1.0):
            return Vector(self.x * other, self.y * other, self.z * other)
    
    def __rmul__(self, other):
        """ Called if 4*self for instance """
        return self.__mul__(other)
            
    def __div__(self, other):
        if type(other) == type(1) or type(other) == type(1.0):
            return Vector(self.x/other, self.y/other, self.z/other)
    
    def __add__(self, other):
        """ Returns the vector addition of self and other """
        return Vector(self.x+other.x, self.y+other.y, self.z+other.z)
    
    def __sub__(self, other):
        """ Returns the vector difference of self and other """
        return Vector(self.x-other.x, self.y-other.y, self.z-other.z)
        
    def __repr__(self):
        str1=''
        str1 = str1+'x: '+str(self.x)+' y: '+str(self.y)+' z: '+str(self.z)
        return str1

if(__name__ == "__main__"):
    v = Vector(0,1,0)
    v = v.rotate(90)
    print(v)