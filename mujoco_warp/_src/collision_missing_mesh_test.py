"""Collision regression for absent per-world and broadcast mesh slots."""

import mujoco
import numpy as np
import warp as wp
from absl.testing import absltest
from absl.testing import parameterized

import mujoco_warp as mjw
from mujoco_warp import BroadphaseType

_XML = """<mujoco><asset><mesh name="cube" vertex="-.1 -.1 -.1 -.1 -.1 .1 -.1 .1 -.1 -.1 .1 .1 .1 -.1 -.1 .1 -.1 .1 .1 .1 -.1 .1 .1 .1"/></asset><worldbody><geom name="floor" type="plane" size="1 1 .1"/><body name="object" pos="0 0 .09"><freejoint/><geom name="slot" type="mesh" mesh="cube"/></body><body name="robot" pos=".05 0 .1"><freejoint/><geom name="probe" type="sphere" size=".08"/></body></worldbody></mujoco>"""


class MissingMeshTest(parameterized.TestCase):
  @parameterized.product(
    broadphase=[BroadphaseType.NXN, BroadphaseType.SAP_TILE],
    layout=["single_missing", "broadcast_missing", "mixed", "broadcast_valid"],
  )
  def test_missing_mesh_contacts(self, broadphase, layout):
    model = mujoco.MjModel.from_xml_string(_XML)
    slot, probe, floor = (model.geom(name).id for name in ("slot", "probe", "floor"))
    nworld = 1 if layout == "single_missing" else 2
    wp_model = mjw.put_model(model)
    wp_model.opt.broadphase = broadphase
    dataid = np.tile(model.geom_dataid, (2 if layout == "mixed" else 1, 1))
    if layout != "broadcast_valid":
      dataid[0, slot] = -1
    wp_model.geom_dataid = wp.array(dataid, dtype=int)
    data = mjw.make_data(model, nworld=nworld, nconmax=64, njmax=64)
    mjw.kinematics(wp_model, data)
    mjw.collision(wp_model, data)
    wp.synchronize()
    count = int(data.nacon.numpy()[0])
    pairs = data.contact.geom.numpy()[:count]
    worlds = data.contact.worldid.numpy()[:count]
    for world in range(nworld):
      contacts = {tuple(sorted(map(int, pair))) for pair in pairs[worlds == world]}
      if dataid[world % len(dataid), slot] < 0:
        self.assertFalse(any(slot in pair for pair in contacts))
      else:
        self.assertIn(tuple(sorted((slot, probe))), contacts)
        self.assertIn(tuple(sorted((slot, floor))), contacts)


if __name__ == "__main__":
  absltest.main()
