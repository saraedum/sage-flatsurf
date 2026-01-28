r"""
Flow decompositions of surfaces into cylinders and minimal components.

EXAMPLES::

    sage: from flatsurf import translation_surfaces
    sage: S = translation_surfaces.regular_octagon()

    sage: direction = next(iter(S.slopes()))  # optional: pyflatsurf
    sage: decomposition = S.flow_decomposition(direction)  # optional: pyflatsurf

    sage: decomposition  # optional: pyflatsurf
    Flow decomposition of Translation Surface in H_2(2) built from a regular octagon into 1 undetermined component

    sage: decomposition.decompose()  # optional: pyflatsurf
    sage: decomposition  # optional: pyflatsurf
    Flow decomposition of Translation Surface in H_2(2) built from a regular octagon into 2 cylinders

"""

# ********************************************************************
#  This file is part of sage-flatsurf.
#
#        Copyright (C) 2026 Julian Rüth
#
#  sage-flatsurf is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  sage-flatsurf is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with sage-flatsurf. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************

from sage.structure.sage_object import SageObject
from sage.misc.cachefunc import cached_method
from sage.misc.unknown import UnknownClass, Unknown


class FlowDecomposition_base(SageObject):
    r"""
    Base class for flow decompositions of a surface.

    EXAMPLES::

        sage: from flatsurf import translation_surfaces
        sage: S = translation_surfaces.regular_octagon()

        sage: direction = next(iter(S.slopes()))  # optional: pyflatsurf
        sage: decomposition = S.flow_decomposition(direction)  # optional: pyflatsurf

    TESTS::

        sage: from flatsurf.geometry.flow_decomposition import FlowDecomposition_base
        sage: isinstance(decomposition, FlowDecomposition_base)  # optional: pyflatsurf
        True

    """
    def __init__(self, surface, direction):
        from flatsurf.geometry.categories.translation_surfaces import TranslationSurfaces
        if surface not in TranslationSurfaces():
            raise NotImplementedError("surface must be a translation surface")

        if not direction or direction not in surface.base_ring() ** 2:
            raise TypeError("direction must a direction in the surface")


        self._surface = surface
        self._direction = direction

    def surface(self):
        return self._surface

    def direction(self):
        return self._direction

    def _repr_(self):
        r"""
        Return a printable representation of this decomposition.

        EXAMPLES::

            sage: from flatsurf import translation_surfaces
            sage: S = translation_surfaces.regular_octagon()

            sage: direction = next(iter(S.slopes()))  # optional: pyflatsurf
            sage: S.flow_decomposition(direction)  # optional: pyflatsurf
            Flow decomposition of Translation Surface in H_2(2) built from a regular octagon into 1 undetermined component
            
        """
        components = []

        cylinders = len(self.cylinders())
        if cylinders:
            components.append(f"{cylinders} cylinder{'s' if cylinders > 1 else ''}")

        minimals = len(self.minimal_components())
        if minimals:
            components.append(f"{minimals} mininmal component{'s' if minimals > 1 else ''}")

        undetermineds = len(self.undetermined_components())
        if undetermineds:
            components.append(f"{undetermineds} undetermined component{'s' if undetermineds > 1 else ''}")

        return f"Flow decomposition of {self._surface} into {'and'.join(components)}"

    def cylinders(self):
        r"""
        Return the cylinders components in this decomposition.

        EXAMPLES::

            sage: from flatsurf import translation_surfaces
            sage: S = translation_surfaces.regular_octagon()

            sage: direction = next(iter(S.slopes()))  # optional: pyflatsurf
            sage: decomposition = S.flow_decomposition(direction)  # optional: pyflatsurf
            sage: decomposition.decompose()

            sage: decomposition.cylinders()
            [Cylinder component, Cylinder component]

        """
        return [c for c in self.components() if c.is_cylinder() == True]

    def minimal_components(self):
        r"""
        Return the minimal components in this decomposition.

        EXAMPLES::

            sage: from flatsurf import translation_surfaces
            sage: S = translation_surfaces.regular_octagon()

            sage: direction = next(iter(S.slopes()))  # optional: pyflatsurf
            sage: decomposition = S.flow_decomposition(direction)  # optional: pyflatsurf
            sage: decomposition.decompose()

            sage: decomposition.minimal_components()
            []

        """
        return [c for c in self.components() if c.is_minimal() == True]

    def undetermined_components(self):
        r"""
        Return the undetermined components in this decomposition.

        EXAMPLES::

            sage: from flatsurf import translation_surfaces
            sage: S = translation_surfaces.regular_octagon()

            sage: direction = next(iter(S.slopes()))  # optional: pyflatsurf
            sage: decomposition = S.flow_decomposition(direction)  # optional: pyflatsurf

            sage: decomposition.undetermined_components()
            [Undetermined component]

            sage: decomposition.decompose()
            sage: decomposition.undetermined_components()
            []

        """
        return [c for c in self.components() if c.is_undetermined()]

    def components(self) -> list["FlowComponent_base"]:
        raise NotImplementedError

    def decompose(self, limit=None):
        raise NotImplementedError


class FlowDecomposition(FlowDecomposition_base):
    r"""
    A flow decomposition on a native sage-flatsurf surface.

    EXAMPLES::

        sage: from flatsurf import translation_surfaces
        sage: S = translation_surfaces.regular_octagon()

        sage: direction = next(iter(S.slopes()))  # optional: pyflatsurf
        sage: decomposition = S.flow_decomposition(direction)  # optional: pyflatsurf

    TESTS::

        sage: from flatsurf.geometry.flow_decomposition import FlowDecomposition
        sage: isinstance(decomposition, FlowDecomposition)  # optional: pyflatsurf
        True

    """
    def __init__(self, surface, direction):
        super().__init__(surface, direction)


    @cached_method
    def _backend(self):
        to_backend = self.surface().pyflatsurf()
        return to_backend, to_backend.codomain().flow_decomposition(self._direction)

    def components(self) -> list["FlowComponent_base"]:
        to_backend, backend = self._backend()
        return [FlowComponent_mapped(self, component, to_backend.section()) for component in backend.components()]

    def decompose(self, limit=None):
        _, backend = self._backend()
        backend.decompose(limit=limit)


class FlowComponent_base(SageObject):
    def __init__(self, parent: FlowDecomposition_base):
        pass

    def is_cylinder(self) -> bool | UnknownClass:
        raise NotImplementedError

    def is_minimal(self) -> bool | UnknownClass:
        raise NotImplementedError

    def is_undetermined(self) -> bool:
        raise NotImplementedError

    def area(self):
        raise NotImplementedError

    def _repr_(self):
        if self.is_cylinder() == True:
            return "Cylinder component"
        if self.is_minimal() == True:
            return "Minimal component"
        return "Undetermined component"

class FlowComponent_mapped(FlowComponent_base):
    def __init__(self, parent: FlowDecomposition_base, component: FlowComponent_base, morphism):
        super().__init__(parent)

        self._component = component

    def is_cylinder(self):
        return self._component.is_cylinder()

    def is_minimal(self):
        return self._component.is_minimal()

    def is_undetermined(self):
        return self._component.is_undetermined()
