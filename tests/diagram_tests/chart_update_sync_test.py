from drawpyo.diagram.objects import Object
from drawpyo.diagram_types.bar_chart import BarChart
from drawpyo.diagram_types.pie_chart import PieChart
from drawpyo.diagram_types.legend import Legend
from drawpyo.page import Page


def assert_page_matches_group(page, group):
    assert all(obj in page.objects for obj in group.objects)


def assert_old_objects_removed(page, old_objects):
    assert all(obj not in page.objects for obj in old_objects)


def test_bar_chart_update_data_syncs_attached_pages():
    chart = BarChart({"A": 10, "B": 20})
    page_one = Page()
    page_two = Page()
    unrelated = Object(value="unrelated", position=(0, 0), width=10, height=10)
    page_one.add_object(unrelated)

    chart.add_to_page(page_one)
    chart.add_to_page(page_two)
    chart.add_to_page(page_one)
    old_objects = list(chart.group.objects)

    chart.update_data({"X": 5, "Y": 15, "Z": 25})

    assert_old_objects_removed(page_one, old_objects)
    assert_old_objects_removed(page_two, old_objects)
    assert_page_matches_group(page_one, chart.group)
    assert_page_matches_group(page_two, chart.group)
    assert unrelated in page_one.objects


def test_bar_chart_update_colors_syncs_attached_page():
    chart = BarChart({"A": 10, "B": 20})
    page = Page()
    chart.add_to_page(page)
    old_objects = list(chart.group.objects)

    chart.update_colors(["#ff0000", "#00ff00"])

    assert_old_objects_removed(page, old_objects)
    assert_page_matches_group(page, chart.group)


def test_pie_chart_update_data_syncs_attached_pages():
    chart = PieChart({"A": 10, "B": 20})
    page_one = Page()
    page_two = Page()
    chart.add_to_page(page_one)
    chart.add_to_page(page_two)
    old_objects = list(chart.group.objects)

    chart.update_data({"X": 10, "Y": 20, "Z": 30})

    assert_old_objects_removed(page_one, old_objects)
    assert_old_objects_removed(page_two, old_objects)
    assert_page_matches_group(page_one, chart.group)
    assert_page_matches_group(page_two, chart.group)


def test_pie_chart_update_colors_syncs_attached_page():
    chart = PieChart({"A": 10, "B": 20})
    page = Page()
    chart.add_to_page(page)
    old_objects = list(chart.group.objects)

    chart.update_colors(["#ff0000", "#00ff00"])

    assert_old_objects_removed(page, old_objects)
    assert_page_matches_group(page, chart.group)


def test_legend_update_mapping_syncs_attached_pages():
    legend = Legend({"A": "#ff0000", "B": "#00ff00"})
    page_one = Page()
    page_two = Page()
    legend.add_to_page(page_one)
    legend.add_to_page(page_two)
    old_objects = list(legend.group.objects)

    legend.update_mapping(
        {"First": "#0000ff", "Second": "#ffff00", "Third": "#00ffff"}
    )

    assert_old_objects_removed(page_one, old_objects)
    assert_old_objects_removed(page_two, old_objects)
    assert_page_matches_group(page_one, legend.group)
    assert_page_matches_group(page_two, legend.group)


def test_repeated_updates_keep_page_synchronized():
    chart = BarChart({"A": 10})
    page = Page()
    chart.add_to_page(page)

    for data in ({"B": 20, "C": 30}, {"D": 40}, {"E": 50, "F": 60, "G": 70}):
        old_objects = list(chart.group.objects)
        chart.update_data(data)
        assert_old_objects_removed(page, old_objects)
        assert_page_matches_group(page, chart.group)
