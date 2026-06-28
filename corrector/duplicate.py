"""
重复文本去除纠错器。

利用 Overlap Window 的特性，
去除相邻两次识别结果中的重复文本。
"""

from __future__ import annotations

from core.sentence import Sentence
from corrector.base import BaseCorrector


class DuplicateCorrector(BaseCorrector):
    """
    重复文本去除纠错器。

    保留上一次原始识别文本，
    用后缀-前缀匹配找出重叠部分并去除。
    """

    def __init__(self) -> None:
        self._prev_text = ""

    def correct(self, sentence: Sentence) -> Sentence:
        """
        去除与上一次识别结果重复的文本前缀。

        Parameters
        ----------
        sentence
            待处理文本。

        Returns
        -------
        Sentence
            去除重复后的文本。
        """
        text = sentence.text.strip()

        if not self._prev_text or not text:
            self._prev_text = text
            return sentence

        # 找 prev_text 后缀与 text 前缀的最长匹配
        # 倒序遍历，首次命中即最长
        max_overlap = min(len(self._prev_text), len(text))
        overlap_len = 0
        for i in range(max_overlap, 0, -1):
            if self._prev_text[-i:] == text[:i]:
                overlap_len = i
                break

        if overlap_len > 0:
            text = text[overlap_len:].strip()

        self._prev_text = text
        sentence.text = text
        return sentence

