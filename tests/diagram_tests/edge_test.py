"""
Tests for the Edge class.

Edges represent connections (arrows, lines) between objects in a diagram.
"""

import pytest
import drawpyo
from drawpyo.diagram.edges import Edge, EdgeGeometry, EdgeLabel, Point
from drawpyo.utils.color_scheme import ColorScheme


class TestEdgeInit:
    """Edge object initialization tests"""

    def test_default_values(self, empty_page: drawpyo.Page) -> None:
        """Checks default values when creating Edge"""
        edge = Edge(page=empty_page)

        assert edge.xml_class == "mxCell"
        assert edge.waypoints == "orthogonal"
        assert edge.connection == "line"
        assert edge.pattern == "solid"
        assert edge.edge == 1

    def test_with_source_and_target(
        self, empty_page: drawpyo.Page, basic_object: drawpyo.diagram.Object
    ) -> None:
        """Checks Edge creation with source and target"""
        obj1 = drawpyo.diagram.Object(page=empty_page, value="Object 1")
        obj2 = drawpyo.diagram.Object(page=empty_page, value="Object 2")

        edge = Edge(page=empty_page, source=obj1, target=obj2)

        assert edge.source == obj1
        assert edge.target == obj2
        assert edge in obj1.out_edges
        assert edge in obj2.in_edges

    def test_with_label(self, empty_page: drawpyo.Page) -> None:
        """Checks if Edge is created with a label"""
        edge = Edge(page=empty_page, label="Connection")
        assert edge.label == "Connection"

    def test_with_waypoints(self, empty_page: drawpyo.Page) -> None:
        """Tests Edge creation with different waypoints"""
        edge_orthogonal = Edge(page=empty_page, waypoints="orthogonal")
        assert edge_orthogonal.waypoints == "orthogonal"

        edge_straight = Edge(page=empty_page, waypoints="straight")
        assert edge_straight.waypoints == "straight"

        edge_curved = Edge(page=empty_page, waypoints="curved")
        assert edge_curved.waypoints == "curved"


class TestEdgeLineStyles:
    """Edge Line Style Tests"""

    def test_pattern_solid(self, empty_page: drawpyo.Page) -> None:
        """Checks for a solid line"""
        edge = Edge(page=empty_page, pattern="solid")
        assert edge.pattern == "solid"

    def test_pattern_dashed(self, empty_page: drawpyo.Page) -> None:
        """Checks the dotted line"""
        edge = Edge(page=empty_page, pattern="dashed_small")
        assert edge.pattern == "dashed_small"

    def test_pattern_dotted(self, empty_page: drawpyo.Page) -> None:
        """Checks the dotted line"""
        edge = Edge(page=empty_page, pattern="dotted_small")
        assert edge.pattern == "dotted_small"

    def test_stroke_width(self, empty_page: drawpyo.Page) -> None:
        """Checks the line width setting"""
        edge = Edge(page=empty_page, strokeWidth=3)
        assert edge.strokeWidth == 3

    def test_stroke_color(self, empty_page: drawpyo.Page) -> None:
        """Checks the line color setting"""
        edge = Edge(page=empty_page, stroke_color="#FF0000")
        assert edge.strokeColor == "#FF0000"


class TestEdgeLineEnds:
    """Edge line end (arrow) tests"""

    def test_line_end_target(self, empty_page: drawpyo.Page) -> None:
        """Checks the installation of the arrow at the end"""
        edge = Edge(page=empty_page, line_end_target="classic")
        assert edge.line_end_target == "classic"

    def test_line_end_source(self, empty_page: drawpyo.Page) -> None:
        """Checks the arrow position at the start"""
        edge = Edge(page=empty_page, line_end_source="classic")
        assert edge.line_end_source == "classic"

    def test_bidirectional_arrows(self, empty_page: drawpyo.Page) -> None:
        """Checks for bidirectional arrows"""
        edge = Edge(
            page=empty_page,
            line_end_target="classic",
            line_end_source="classic",
        )
        assert edge.line_end_target == "classic"
        assert edge.line_end_source == "classic"

    def test_end_fill_target(self, empty_page: drawpyo.Page) -> None:
        """Checks the fill of the arrow at the end"""
        edge = Edge(page=empty_page, endFill_target=True)
        assert edge.endFill_target is True

    def test_end_fill_source(self, empty_page: drawpyo.Page) -> None:
        """Checks the fill of the arrow at the start"""
        edge = Edge(page=empty_page, endFill_source=True)
        assert edge.endFill_source is True

    def test_end_size(self, empty_page: drawpyo.Page) -> None:
        """Checks the size of the arrow at the end"""
        edge = Edge(page=empty_page, endSize=12)
        assert edge.endSize == 12

    def test_start_size(self, empty_page: drawpyo.Page) -> None:
        """Checks the size of the arrow at the start"""
        edge = Edge(page=empty_page, startSize=10)
        assert edge.startSize == 10


class TestEdgeGeometry:
    """Edge Geometry Tests"""

    def test_entry_exit_points(self, empty_page: drawpyo.Page) -> None:
        """Checks entry and exit points"""
        edge = Edge(
            page=empty_page,
            entryX=0.5,
            entryY=1.0,
            exitX=0.5,
            exitY=0.0,
        )
        assert edge.entryX == 0.5
        assert edge.entryY == 1.0
        assert edge.exitX == 0.5
        assert edge.exitY == 0.0

    def test_entry_exit_offsets(self, empty_page: drawpyo.Page) -> None:
        """Checks the offsets of entry and exit points"""
        edge = Edge(
            page=empty_page,
            entryDx=10,
            entryDy=20,
            exitDx=15,
            exitDy=25,
        )
        assert edge.entryDx == 10
        assert edge.entryDy == 20
        assert edge.exitDx == 15
        assert edge.exitDy == 25

    def test_jetty_size_auto(self, empty_page: drawpyo.Page) -> None:
        """Checks the automatic size of jetty"""
        edge = Edge(page=empty_page, jettySize="auto")
        assert edge.jettySize == "auto"

    def test_jetty_size_numeric(self, empty_page: drawpyo.Page) -> None:
        """Checks the numeric size of jetty"""
        edge = Edge(page=empty_page, jettySize=20)
        assert edge.jettySize == 20

    def test_perimeter_spacing(self, empty_page: drawpyo.Page) -> None:
        """Checks the indents from the perimeter"""
        edge = Edge(
            page=empty_page,
            targetPerimeterSpacing=10,
            sourcePerimeterSpacing=15,
        )
        assert edge.targetPerimeterSpacing == 10
        assert edge.sourcePerimeterSpacing == 15


class TestEdgeLabels:
    """Edge tag tests"""

    def test_label_basic(self, empty_page: drawpyo.Page) -> None:
        """Checks the base label"""
        edge = Edge(page=empty_page, label="Test Label")
        assert edge.label == "Test Label"

    def test_label_position(self, empty_page: drawpyo.Page) -> None:
        """Checks the position of a mark along a line"""
        edge = Edge(page=empty_page, label="Label", label_position=0.5)
        assert edge.label_position == 0.5

    def test_label_offset(self, empty_page: drawpyo.Page) -> None:
        """Checks the offset of the mark from the line"""
        edge = Edge(page=empty_page, label="Label", label_offset=10)
        assert edge.label_offset == 10

    def test_label_at_source(self, empty_page: drawpyo.Page) -> None:
        """Checks the label at the source"""
        edge = Edge(page=empty_page, label="Source", label_position=-1.0)
        assert edge.label_position == -1.0

    def test_label_at_target(self, empty_page: drawpyo.Page) -> None:
        """Checks the target's mark"""
        edge = Edge(page=empty_page, label="Target", label_position=1.0)
        assert edge.label_position == 1.0


class TestEdgeColors:
    """Edge Color Tests"""

    def test_stroke_color_hex(self, empty_page: drawpyo.Page) -> None:
        """Checks the hex color of the stroke"""
        edge = Edge(page=empty_page, stroke_color="#FF0000")
        assert edge.strokeColor == "#FF0000"

    def test_fill_color_hex(self, empty_page: drawpyo.Page) -> None:
        """Checks the hex fill color"""
        edge = Edge(page=empty_page, fill_color="#00FF00")
        assert edge.fillColor == "#00FF00"

    def test_color_scheme(
        self, empty_page: drawpyo.Page, basic_color_scheme: ColorScheme
    ) -> None:
        """Checks the application of the color scheme"""
        edge = Edge(page=empty_page, color_scheme=basic_color_scheme)
        assert edge.color_scheme == basic_color_scheme
        assert edge.strokeColor == basic_color_scheme.stroke_color

    def test_opacity(self, empty_page: drawpyo.Page) -> None:
        """Checks the transparency setting"""
        edge = Edge(page=empty_page, opacity=50)
        assert edge.opacity == 50


class TestEdgeEffects:
    """Edge special effects tests"""

    def test_rounded(self, empty_page: drawpyo.Page) -> None:
        """Checks for rounded corners"""
        edge = Edge(page=empty_page, rounded=1)
        assert edge.rounded == 1

    def test_shadow(self, empty_page: drawpyo.Page) -> None:
        """Checks the shadow"""
        edge = Edge(page=empty_page, shadow=True)
        assert edge.shadow is True

    def test_sketch(self, empty_page: drawpyo.Page) -> None:
        """Checks the sketch effect"""
        edge = Edge(page=empty_page, sketch=True)
        assert edge.sketch is True

    def test_flow_animation(self, empty_page: drawpyo.Page) -> None:
        """Checks the flow animation"""
        edge = Edge(page=empty_page, flowAnimation=True)
        assert edge.flowAnimation is True


class TestEdgeConnectionStyles:
    """Edge connection style tests"""

    def test_connection_line(self, empty_page: drawpyo.Page) -> None:
        """Checks the line connection"""
        edge = Edge(page=empty_page, connection="line")
        assert edge.connection == "line"

    def test_connection_link(self, empty_page: drawpyo.Page) -> None:
        """Checks the link connection"""
        edge = Edge(page=empty_page, connection="link")
        assert edge.connection == "link"

    def test_connection_arrow(self, empty_page: drawpyo.Page) -> None:
        """Checks the arrow connection"""
        edge = Edge(page=empty_page, connection="arrow")
        assert edge.connection == "arrow"


class TestEdgeJumps:
    """Tests of line jumps at intersections"""

    def test_jump_style_arc(self, empty_page: drawpyo.Page) -> None:
        """Tests the arc jump style"""
        edge = Edge(page=empty_page, jumpStyle="arc")
        assert edge.jumpStyle == "arc"

    def test_jump_style_gap(self, empty_page: drawpyo.Page) -> None:
        """Tests the gap jump style"""
        edge = Edge(page=empty_page, jumpStyle="gap")
        assert edge.jumpStyle == "gap"

    def test_jump_style_sharp(self, empty_page: drawpyo.Page) -> None:
        """Tests the sharp jumping style"""
        edge = Edge(page=empty_page, jumpStyle="sharp")
        assert edge.jumpStyle == "sharp"

    def test_jump_size(self, empty_page: drawpyo.Page) -> None:
        """Checks the jump size"""
        edge = Edge(page=empty_page, jumpSize=12)
        assert edge.jumpSize == 12


class TestEdgeRemoval:
    """Edge removal tests"""

    def test_remove_edge(self, empty_page: drawpyo.Page) -> None:
        """Checks for Edge removal"""
        obj1 = drawpyo.diagram.Object(page=empty_page, value="Object 1")
        obj2 = drawpyo.diagram.Object(page=empty_page, value="Object 2")
        edge = Edge(page=empty_page, source=obj1, target=obj2)

        assert edge in obj1.out_edges
        assert edge in obj2.in_edges

        edge.remove()

        assert edge not in obj1.out_edges
        assert edge not in obj2.in_edges

    def test_detach_from_source(self, empty_page: drawpyo.Page) -> None:
        """Checks detachment from source via del"""
        obj1 = drawpyo.diagram.Object(page=empty_page, value="Object 1")
        obj2 = drawpyo.diagram.Object(page=empty_page, value="Object 2")
        edge = Edge(page=empty_page, source=obj1, target=obj2)

        assert edge in obj1.out_edges
        # Use del to detach
        del edge.source

        assert edge.source is None

    def test_detach_from_target(self, empty_page: drawpyo.Page) -> None:
        """Checks detachment from target via del"""
        obj1 = drawpyo.diagram.Object(page=empty_page, value="Object 1")
        obj2 = drawpyo.diagram.Object(page=empty_page, value="Object 2")
        edge = Edge(page=empty_page, source=obj1, target=obj2)

        assert edge in obj2.in_edges
        # Use del to detach
        del edge.target

        assert edge.target is None


class TestEdgeReassignment:
    """Edge source and target reassignment tests"""

    def test_reassign_source(self, empty_page: drawpyo.Page) -> None:
        """Checks source reassignment"""
        obj1 = drawpyo.diagram.Object(page=empty_page, value="Object 1")
        obj2 = drawpyo.diagram.Object(page=empty_page, value="Object 2")
        obj3 = drawpyo.diagram.Object(page=empty_page, value="Object 3")

        edge = Edge(page=empty_page, source=obj1, target=obj2)

        assert edge in obj1.out_edges
        assert edge not in obj3.out_edges

        edge.source = obj3

        # Check that the new source is installed and edge is in its list.
        assert edge in obj3.out_edges
        assert edge.source == obj3

    def test_reassign_target(self, empty_page: drawpyo.Page) -> None:
        """Checks target reassignment"""
        obj1 = drawpyo.diagram.Object(page=empty_page, value="Object 1")
        obj2 = drawpyo.diagram.Object(page=empty_page, value="Object 2")
        obj3 = drawpyo.diagram.Object(page=empty_page, value="Object 3")

        edge = Edge(page=empty_page, source=obj1, target=obj2)

        assert edge in obj2.in_edges
        assert edge not in obj3.in_edges

        edge.target = obj3

        # Check that the new target is installed and edge is in its list.
        assert edge in obj3.in_edges
        assert edge.target == obj3


class TestEdgeRepresentation:
    """Edge string representation tests"""

    def test_repr_basic(self, empty_page: drawpyo.Page) -> None:
        """Checks the underlying string representation"""
        obj1 = drawpyo.diagram.Object(page=empty_page, value="Start")
        obj2 = drawpyo.diagram.Object(page=empty_page, value="End")
        edge = Edge(page=empty_page, source=obj1, target=obj2)

        repr_str = repr(edge)

        assert "Edge" in repr_str
        assert "Start" in repr_str
        assert "End" in repr_str

    def test_repr_with_label(self, empty_page: drawpyo.Page) -> None:
        """Checks the view with the label"""
        obj1 = drawpyo.diagram.Object(page=empty_page, value="Start")
        obj2 = drawpyo.diagram.Object(page=empty_page, value="End")
        edge = Edge(page=empty_page, source=obj1, target=obj2, label="Connection")

        repr_str = repr(edge)

        assert "Connection" in repr_str


class TestEdgeGeometryClass:
    """EdgeGeometry class tests"""

    def test_edge_geometry_init(self) -> None:
        """Checks the initialization of EdgeGeometry"""
        geom = EdgeGeometry()
        assert isinstance(geom, EdgeGeometry)

    def test_edge_geometry_has_relative_attribute(self) -> None:
        """Checks if an EdgeGeometry has the relative attribute"""
        geom = EdgeGeometry()
        assert hasattr(geom, "relative")
        assert geom.relative == 1


class TestPointClass:
    """Point class tests"""

    def test_point_init(self) -> None:
        """Checks the initialization of Point"""
        point = Point(x=100, y=200)
        assert point.x == 100
        assert point.y == 200

    def test_point_default_values(self) -> None:
        """Checks the default values of Point"""
        point = Point()
        assert point.x == 0
        assert point.y == 0
