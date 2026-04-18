import ReactECharts from 'echarts-for-react'
import type { UploadMetricDetail } from '../lib/types'

interface Props {
  timeAxis: number[]
  metrics: UploadMetricDetail[]
}

export function MultiMetricChart({ timeAxis, metrics }: Props) {
  const units = Array.from(new Set(metrics.map((metric) => metric.unit || 'value')))

  const option = {
    backgroundColor: 'transparent',
    animation: false,
    tooltip: {
      trigger: 'axis',
      valueFormatter: (value: number | null) =>
        value === null || Number.isNaN(value) ? 'n/a' : value.toFixed(2),
    },
    legend: {
      top: 0,
      textStyle: {
        color: '#d4d8e8',
      },
    },
    grid: {
      top: 64,
      left: 48,
      right: 48 + Math.max(0, units.length - 1) * 40,
      bottom: 60,
    },
    xAxis: {
      type: 'category',
      data: timeAxis,
      name: 'Time (sec)',
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#7e8aa8' } },
      axisLabel: { color: '#b4bdd6' },
      splitLine: { show: false },
    },
    yAxis: units.map((unit, index) => ({
      type: 'value',
      name: unit === 'value' ? '' : unit,
      position: index % 2 === 0 ? 'left' : 'right',
      offset: Math.floor(index / 2) * 48,
      axisLine: { show: true, lineStyle: { color: '#7e8aa8' } },
      axisLabel: { color: '#b4bdd6' },
      splitLine: { lineStyle: { color: 'rgba(126, 138, 168, 0.14)' } },
    })),
    dataZoom: [
      { type: 'inside' },
      {
        type: 'slider',
        bottom: 18,
        borderColor: 'rgba(126, 138, 168, 0.2)',
        textStyle: { color: '#b4bdd6' },
      },
    ],
    series: metrics.map((metric) => ({
      name: metric.unit ? `${metric.display_name} (${metric.unit})` : metric.display_name,
      type: 'line',
      yAxisIndex: units.indexOf(metric.unit || 'value'),
      showSymbol: false,
      smooth: false,
      connectNulls: false,
      lineStyle: {
        width: 2,
      },
      data: metric.values,
    })),
  }

  return <ReactECharts option={option} style={{ height: 480, width: '100%' }} />
}
