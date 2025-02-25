#!/usr/bin/env python3
# Copyright (C) 2020 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest

from livestatus import SiteId

from cmk.utils.hostaddress import HostName

import cmk.gui.graphing._graph_templates as gt
from cmk.gui.config import active_config
from cmk.gui.graphing._expression import (
    Constant,
    CriticalOf,
    Difference,
    MaximumOf,
    Metric,
    parse_expression,
    WarningOf,
)
from cmk.gui.graphing._graph_specification import (
    GraphMetric,
    GraphRecipe,
    MetricOpConstant,
    MetricOperation,
    MetricOpOperator,
    MetricOpRRDSource,
    MinimalVerticalRange,
)
from cmk.gui.graphing._graph_templates import TemplateGraphSpecification
from cmk.gui.graphing._graph_templates_from_plugins import (
    GraphTemplate,
    MetricDefinition,
    MetricUnitColor,
    MinimalGraphTemplateRange,
    ScalarDefinition,
)
from cmk.gui.graphing._utils import parse_perf_data, translate_metrics

from cmk.ccc.exceptions import MKGeneralException


@pytest.mark.parametrize(
    "expression, result",
    [
        (
            "fs_size,fs_used,-",
            MetricOpOperator(
                operator_name="-",
                operands=[
                    MetricOpRRDSource(
                        site_id=SiteId(""),
                        host_name=HostName(""),
                        service_name="",
                        metric_name="fs_size",
                        consolidation_func_name=None,
                        scale=1048576,
                    ),
                    MetricOpRRDSource(
                        site_id=SiteId(""),
                        host_name=HostName(""),
                        service_name="",
                        metric_name="_",
                        consolidation_func_name=None,
                        scale=1048576,
                    ),
                ],
            ),
        ),
        (
            "fs_growth.min,0,MIN,-1,*",
            MetricOpOperator(
                operator_name="*",
                operands=[
                    MetricOpOperator(
                        operator_name="MIN",
                        operands=[
                            MetricOpRRDSource(
                                site_id=SiteId(""),
                                host_name=HostName(""),
                                service_name="",
                                metric_name="growth",
                                consolidation_func_name="min",
                                scale=12.136296296296296,
                            ),
                            MetricOpConstant(value=0.0),
                        ],
                    ),
                    MetricOpConstant(value=-1.0),
                ],
            ),
        ),
    ],
)
def test_rpn_stack(expression: str, result: MetricOperation) -> None:
    perf_data, check_command = parse_perf_data(
        "/=163651.992188;;;; fs_size=477500.03125;;;; growth=-1280.489081;;;;",
        "check_mk-df",
        config=active_config,
    )
    translated_metrics = translate_metrics(perf_data, check_command)
    lq_row = {"site": "", "host_name": "", "service_description": ""}
    assert (
        gt.metric_expression_to_graph_recipe_expression(
            parse_expression(expression, translated_metrics), translated_metrics, lq_row, None
        )
        == result
    )


def test_create_graph_recipe_from_template() -> None:
    graph_template = GraphTemplate(
        id="my_id",
        title="",
        metrics=[
            MetricDefinition(
                expression=Metric("fs_used"),
                line_type="area",
            ),
            MetricDefinition(
                expression=Difference(
                    minuend=Metric("fs_size"),
                    subtrahend=Metric("fs_used"),
                    explicit_color="#e3fff9",
                ),
                line_type="stack",
                title="Free space",
            ),
            MetricDefinition(
                expression=Metric("fs_size"),
                line_type="line",
            ),
        ],
        scalars=[
            ScalarDefinition(
                expression=WarningOf(Metric("fs_used")),
                title="Warning",
            ),
            ScalarDefinition(
                expression=CriticalOf(Metric("fs_used")),
                title="Critical",
            ),
        ],
        conflicting_metrics=["fs_free"],
        optional_metrics=[],
        consolidation_function=None,
        range=MinimalGraphTemplateRange(min=Constant(0), max=MaximumOf(Metric("fs_used"))),
        omit_zero_metrics=False,
    )
    perf_data, check_command = parse_perf_data(
        "/=163651.992188;;;; fs_size=477500.03125;;;; growth=-1280.489081;;;;",
        "check_mk-df",
        config=active_config,
    )
    translated_metrics = translate_metrics(perf_data, check_command)
    lq_row = {"site": "", "host_name": "", "service_description": ""}
    specification = TemplateGraphSpecification(
        site=SiteId("Site"),
        host_name=HostName("Host-Name"),
        service_description="Service name",
    )

    assert gt.create_graph_recipe_from_template(
        graph_template, translated_metrics, lq_row, specification
    ) == GraphRecipe(
        title="Used space",
        unit="IECNotation_B_AutoPrecision_2",
        explicit_vertical_range=MinimalVerticalRange(type="minimal", min=0.0, max=None),
        horizontal_rules=[],
        omit_zero_metrics=False,
        consolidation_function="max",
        metrics=[
            GraphMetric(
                title="Used space",
                line_type="area",
                operation=MetricOpRRDSource(
                    site_id=SiteId(""),
                    host_name=HostName(""),
                    service_name="",
                    metric_name="_",
                    consolidation_func_name="max",
                    scale=1048576.0,
                ),
                unit="IECNotation_B_AutoPrecision_2",
                color="#1e90ff",
            ),
            GraphMetric(
                title="Free space",
                line_type="stack",
                operation=MetricOpOperator(
                    operator_name="-",
                    operands=[
                        MetricOpRRDSource(
                            site_id=SiteId(""),
                            host_name=HostName(""),
                            service_name="",
                            metric_name="fs_size",
                            consolidation_func_name="max",
                            scale=1048576.0,
                        ),
                        MetricOpRRDSource(
                            site_id=SiteId(""),
                            host_name=HostName(""),
                            service_name="",
                            metric_name="_",
                            consolidation_func_name="max",
                            scale=1048576.0,
                        ),
                    ],
                ),
                unit="IECNotation_B_AutoPrecision_2",
                color="#e3fff9",
            ),
            GraphMetric(
                title="Total size",
                line_type="line",
                operation=MetricOpRRDSource(
                    site_id=SiteId(""),
                    host_name=HostName(""),
                    service_name="",
                    metric_name="fs_size",
                    consolidation_func_name="max",
                    scale=1048576.0,
                ),
                unit="IECNotation_B_AutoPrecision_2",
                color="#37fa37",
            ),
        ],
        additional_html=None,
        render_options={},
        data_range=None,
        mark_requested_end_time=False,
        specification=TemplateGraphSpecification(
            site=SiteId("Site"),
            host_name=HostName("Host-Name"),
            service_description="Service name",
            graph_index=None,
            graph_id=None,
            destination=None,
        ),
    )


@pytest.mark.parametrize(
    "expression, perf_data_string, check_command, result_color",
    [
        (
            "load15",
            "load1=0.38;40;80;0;8 load5=0.62;40;80;0;8 load15=0.68;40;80;0;8",
            "check_mk-cpu.loads",
            "#1e1ec8",
        ),
        ("test", "test=5;5;10;0;20", "check_mk-local", "#cc00ff"),
    ],
)
def test_metric_unit_color(
    expression: str, perf_data_string: str, check_command: str | None, result_color: str
) -> None:
    perf_data, check_command = parse_perf_data(
        perf_data_string, check_command, config=active_config
    )
    translated_metrics = translate_metrics(perf_data, check_command)
    translated_metric = translated_metrics.get(expression)
    assert translated_metric is not None
    metric_definition = MetricDefinition(
        expression=parse_expression(expression, translated_metrics),
        line_type="line",
    )
    assert metric_definition.compute_unit_color(translated_metrics, ["test"]) == MetricUnitColor(
        unit=translated_metric.unit_info.id,
        color=result_color,
    )


@pytest.mark.parametrize(
    "expression, perf_data_string, check_command",
    [
        ("test", "", "check_mk-local"),
    ],
)
def test_metric_unit_color_skip(
    expression: str, perf_data_string: str, check_command: str | None
) -> None:
    perf_data, check_command = parse_perf_data(
        perf_data_string, check_command, config=active_config
    )
    translated_metrics = translate_metrics(perf_data, check_command)
    metric_definition = MetricDefinition(
        expression=parse_expression(expression, translated_metrics),
        line_type="line",
    )
    assert metric_definition.compute_unit_color(translated_metrics, ["test"]) is None


@pytest.mark.parametrize(
    "expression, perf_data_string, check_command",
    [
        ("level,altitude,+", "test=5;5;10;0;20", "check_mk-local"),
    ],
)
def test_metric_unit_color_exception(
    expression: str, perf_data_string: str, check_command: str | None
) -> None:
    perf_data, check_command = parse_perf_data(
        perf_data_string, check_command, config=active_config
    )
    translated_metrics = translate_metrics(perf_data, check_command)
    metric_definition = MetricDefinition(
        expression=parse_expression(expression, translated_metrics),
        line_type="line",
    )
    with pytest.raises(MKGeneralException):
        metric_definition.compute_unit_color(translated_metrics, ["test"])
