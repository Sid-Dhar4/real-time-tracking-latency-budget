from pathlib import Path


def test_kitti_label_files_exist():
    for seq in ["0000", "0001"]:
        path = Path(f"tests/fixtures/kitti_tracking/label_02/{seq}.txt")
        assert path.exists(), f"Missing KITTI label file: {path}"
        assert path.stat().st_size > 0


def test_kitti_label_line_has_expected_fields():
    path = Path("tests/fixtures/kitti_tracking/label_02/0000.txt")
    first = path.read_text().splitlines()[0]
    parts = first.split()
    assert len(parts) >= 17
    int(parts[0])
    int(parts[1])
    assert isinstance(parts[2], str)
    float(parts[6])
    float(parts[7])
    float(parts[8])
    float(parts[9])
