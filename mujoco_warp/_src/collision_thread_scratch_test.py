"""Check that worker-local CCD scratch preserves convex contact results."""

import os
from unittest import mock

import mujoco
import numpy as np
import warp as wp
from absl.testing import absltest

import mujoco_warp as mjw

_XML = """<mujoco><option gravity="0 0 0"/><asset><mesh name="cube" vertex="-.1 -.1 -.1 -.1 -.1 .1 -.1 .1 -.1 -.1 .1 .1 .1 -.1 -.1 .1 -.1 .1 .1 .1 -.1 .1 .1 .1"/></asset><worldbody><body pos="0 0 0"><freejoint/><geom type="mesh" mesh="cube"/></body><body pos=".15 0 0"><freejoint/><geom type="mesh" mesh="cube"/></body></worldbody></mujoco>"""


class ThreadScratchTest(absltest.TestCase):
  def test_contacts_match(self):
    model = mujoco.MjModel.from_xml_string(_XML)
    wm = mjw.put_model(model)
    outputs = []
    for flag in ("0", "1"):
      data = mjw.make_data(model, nworld=4, nconmax=64, njmax=64)
      with mock.patch.dict(os.environ, HDMI_CCD_THREAD_SCRATCH=flag):
        mjw.fwd_position(wm, data)
        wp.synchronize()
      n = int(data.nacon.numpy()[0])
      self.assertGreater(n, 0)
      self.assertFalse(data.overflow.numpy().any())
      values = np.column_stack(
        (
          data.contact.worldid.numpy()[:n],
          data.contact.geom.numpy()[:n],
          data.contact.pos.numpy()[:n],
          data.contact.dist.numpy()[:n],
        )
      )
      outputs.append(values[np.lexsort(values.T[::-1])])
    np.testing.assert_allclose(outputs[0], outputs[1], rtol=0, atol=2e-5)


if __name__ == "__main__":
  absltest.main()
