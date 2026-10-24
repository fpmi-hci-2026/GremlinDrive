"""Render reports in the same typography and structure as Labs 1-3."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'shared'))
from report_style import render
render(R,5,'Проектирование прототипа приложения')
render(R.parent/'lab6',6,'Тестирование и оценка качества прототипа приложения')
