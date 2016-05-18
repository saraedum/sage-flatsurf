r"""
Translation Surfaces.
"""
from flatsurf.geometry.cone_surface import ConeSurface_generic, ConeSurface_polygons_and_gluings

from flatsurf.geometry.surface import SurfaceType

from sage.matrix.constructor import matrix, identity_matrix

class TranslationSurface_generic(ConeSurface_generic):
    r"""
    A surface with a flat metric and conical singularities (not necessarily
    multiple angle of pi or 2pi).

    - polygon = polygon + vertex (or equivalently, canonical ordering)

    A translation surface is:

    - field embedded in R
    - index set for the (convex) polygons + favorite polygon
    - edges: ((t1,e1),(t2,e2))

    For finite case:

    - canonical labelings of polygons
    - Delaunay triangulation
    """
    
    def minimal_translation_cover(self):
        return self

    def surface_type(self):
        return SurfaceType.TRANSLATION

    def _check_edge_matrix(self):
        r"""
        Check the compatibility condition
        """
        for lab in self.polygon_labels().some_elements():
            p = self.polygon(lab)
            for e in xrange(p.num_edges()):
                if not self.edge_matrix(lab,e).is_one():
                    raise ValueError("gluings of (%s,%s) is not through translation"%(lab,e))
    
    def edge_matrix(self, p, e=None):
        if e is None:
            p,e = p
        if p not in self.polygon_labels():
            from sage.structure.element import parent
            raise ValueError("p (={!r}) with parent {!r} is not a valid label".format(p,parent(p)))
        elif e < 0 or e >= self.polygon(p).num_edges():
            raise ValueError
        return identity_matrix(self.base_ring(),2)

    def stratum(self):
        r"""
        EXAMPLES::

            sage: import flatsurf.geometry.similarity_surface_generators as sfg
            sage: sfg.translation_surfaces.octagon_and_squares().stratum()
            H(4)
        """
        from sage.dynamics.flat_surfaces.all import AbelianStratum
        from sage.rings.integer_ring import ZZ
        return AbelianStratum([ZZ(a-1) for a in self.angles()])

class TranslationSurface_polygons_and_gluings(
        TranslationSurface_generic,
        ConeSurface_polygons_and_gluings):
    pass

class MinimalTranslationCover(TranslationSurface_generic):
    r"""
    We label copy by cartesian product (polygon from bot, matrix).
    """
    def __init__(self, similarity_surface):
        self._ss = similarity_surface

        from sage.matrix.matrix_space import MatrixSpace
        from sage.categories.cartesian_product import cartesian_product
        from sage.rings.semirings.non_negative_integer_semiring import NN

    def is_finite(self):
        if not self._ss.is_finite():
            return False
        return self._ss.is_rational_cone_surface()

    def base_ring(self):
        return self._ss.base_ring()

    def base_label(self):
        from sage.matrix.constructor import identity_matrix
        I = identity_matrix(self.base_ring(),2)
        I.set_immutable()
        return (self._ss.base_label(), I)

    def polygon(self, lab):
        return lab[1] * self._ss.polygon(lab[0])

    def opposite_edge(self, p, e):
        pp,m = p  # this is the polygon m * ss.polygon(p)
        p2,e2 = self._ss.opposite_edge(pp,e)
        me = self._ss.edge_matrix(pp,e)
        mm = ~me * m
        mm.set_immutable()
        return ((p2,mm),e2)

class AbstractOrigami(TranslationSurface_generic):
    r'''Abstract base class for origamis.
    Realization needs just to define a _domain and four cardinal directions.
    '''

    def up(self, label):
        raise NotImplementedError

    def down(self, label):
        raise NotImplementedError

    def right(self, label):
        raise NotImplementedError

    def left(self, label):
        raise NotImplementedError

    def _repr_(self):
        return "Some AbstractOrigami"

    def is_finite(self):
        return self._domain.is_finite()

    def num_polygons(self):
        r"""
        Returns the number of polygons.
        """
        return self._domain.cardinality()

    def polygon_labels(self):
        return self._domain

    def polygon(self, lab):
        if lab not in self._domain:
            #Updated to print a possibly useful error message
            raise ValueError("Label "+str(lab)+" is not in the domain")
        from flatsurf.geometry.polygon import polygons
        return polygons.square()

    def base_ring(self):
        return QQ

    def opposite_edge(self, p, e):
        if p not in self._domain:
            raise ValueError
        if e==0:
            return self.down(p),2
        if e==1:
            return self.right(p),3
        if e==2:
            return self.up(p),0
        if e==3:
            return self.left(p),1
        raise ValueError
        
        return self._perms[e](p), (e+2)%4


class Origami(AbstractOrigami):
    def __init__(self, r, u, rr=None, uu=None, domain=None):
        if domain is None:
            self._domain = r.parent().domain()
        else:
            self._domain = domain

        self._r = r
        self._u = u
        if rr is None:
            rr = ~r
        else:
            for a in self._domain.some_elements():
                if r(rr(a)) != a:
                    raise ValueError("r o rr is not identity on %s"%a)
                if rr(r(a)) != a:
                    raise ValueError("rr o r is not identity on %s"%a)
        if uu is None:
            uu = ~u
        else:
            for a in self._domain.some_elements():
                if u(uu(a)) != a:
                    raise ValueError("u o uu is not identity on %s"%a)
                if uu(u(a)) != a:
                    raise ValueError("uu o u is not identity on %s"%a)

        self._perms = [uu,r,u,rr] # down,right,up,left

    def opposite_edge(self, p, e):
        if p not in self._domain:
            raise ValueError
        if e < 0 or e > 3:
            raise ValueError
        return self._perms[e](p), (e+2)%4

    def up(self, label):
        return self.opposite_edge(label,2)[0]

    def down(self, label):
        return self.opposite_edge(label,0)[0]

    def right(self, label):
        return self.opposite_edge(label,1)[0]

    def left(self, label):
        return self.opposite_edge(label,3)[0]

    def _repr_(self):
        return "Origami defined by r=%s and u=%s"%(self._r,self._u)


