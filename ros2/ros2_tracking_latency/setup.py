from setuptools import setup

package_name = "ros2_tracking_latency"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Sud",
    maintainer_email="sudheshnad49@gmail.com",
    description="ROS 2 replay wrapper for KITTI tracking benchmark outputs.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "kitti_track_replay = ros2_tracking_latency.kitti_track_replay_node:main",
            "kitti_debug_image_replay = ros2_tracking_latency.kitti_debug_image_replay_node:main",
        ],
    },
)
