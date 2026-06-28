"""
纠错器流水线（责任链）。

将多个纠错器串联执行，
每个纠错器只负责自己的职责。
"""

from __future__ import annotations

from core.sentence import Sentence
from corrector.base import BaseCorrector


class CorrectorPipeline:
    """
    纠错器流水线。

    按顺序执行所有注册的纠错器，
    每个纠错器的输出作为下一个的输入。
    """

    def __init__(self, correctors: list[BaseCorrector]) -> None:
        self._correctors = list(correctors)

    def correct(self, sentence: Sentence) -> Sentence:
        """
        依次执行所有纠错器。

        Parameters
        ----------
        sentence
            待处理文本。

        Returns
        -------
        Sentence
            处理后的文本。
        """
        for corrector in self._correctors:
            sentence = corrector.correct(sentence)
        return sentence
