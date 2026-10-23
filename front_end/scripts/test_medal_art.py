"""资源预算回归：从仓库根目录运行 python -m unittest discover -s front_end/scripts -p test_medal_art.py。"""
from pathlib import Path
import unittest

from PIL import Image


class MedalArtBudgetTests(unittest.TestCase):
    def test_shipped_images_fit_the_low_bandwidth_budget(self):
        root = Path(__file__).resolve().parents[1] / 'public' / 'assets' / 'medals'
        files = list(root.rglob('*.webp'))
        # 256是当前基线；允许继续新增，但删除现有资源需要同步调整基线并说明原因。
        self.assertGreaterEqual(len(files), 256)
        total = 0
        groups = {}
        for path in files:
            with self.subTest(image=str(path.relative_to(root))):
                size = path.stat().st_size
                self.assertLessEqual(size, 4 * 1024)
                total += size
                groups[path.parent] = max(groups.get(path.parent, 0), size)
                with Image.open(path) as image:
                    self.assertEqual(image.format, 'WEBP')
                    self.assertEqual(image.size, (72, 72))
                    self.assertIn('A', image.getbands())
                    image.load()
        self.assertGreaterEqual(len(groups), 33)
        self.assertLessEqual(total, 700 * 1024)
        # 每类取最大的当前档位，覆盖整页；侧栏最多6枚，允许最坏情况全取最大图。
        self.assertLessEqual(sum(groups.values()), 90 * 1024)
        self.assertLessEqual(6 * max(groups.values()), 20 * 1024)


if __name__ == '__main__':
    unittest.main()
