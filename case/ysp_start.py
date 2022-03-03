# -*- coding: utf-8 -*- 
"""Created by ssfanli on 2022/03/03 
"""
import time

from screcord import record
import sys
sys.path.append('.')
from utils.boss import BossHelper
from utils.const import PLATFORM,  PACKAGE, COMMON
from utils.frame import video2frame
from utils.install import Installer
from utils.tools import md, splice, abspath
from utils.uidriver import BaseOperateAND, BaseOperateIOS


class YSPStart(object):

    def __init__(self, platform: str, device_id: str, app_path=None):
        self.plat = platform
        self.did = device_id
        self.pkg_name = PACKAGE.YSP_AND if self.plat == PLATFORM.AND else PACKAGE.YSP_IOS
        self.app_path = app_path
        self.base_dir = md(
            abspath(splice('../output/ysp', 'and' if self.plat == PLATFORM.AND else 'ios')))
        self.bo = None
        self.bh = None

    @property
    def boss_divide_id(self):
        """get divide id

        ios need install and init firstly
        """
        if self.plat == PLATFORM.AND:
            return COMMON.divide_id_mapping[self.did]
        if not self.bo:
            self.app_init()
        return self.bo.get_idfv()

    def download(self, which, version):
        raise NotImplementedError

    def install(self):
        if self.app_path:
            ins = Installer(self.plat, self.did)
            ins.install(self.app_path, self.pkg_name)

    def app_init(self):
        if self.plat == PLATFORM.AND:
            self.bo = BaseOperateAND(self.did, self.pkg_name)
        else:
            self.bo = BaseOperateIOS(self.did, self.pkg_name)

    def boss_init(self):
        """boss_init place after in app_init"""
        self.bh = BossHelper(self.plat, self.boss_divide_id)

    def external_start(self):
        raise NotImplementedError

    def cold_start(self, repeat: int = 10, interval: int = 1):

        def before_test():
            self.install()
            self.app_init()
            self.boss_init()

        def after_test():
            data = self.bh.get_data(page_size=repeat, keyword='app_launch_time', conversion=True)
            self.bh.data_analysis(data)

        def testing(video_fp):

            @video2frame(video_fp)
            @record(self.plat, self.did, video_fp, offset=(1.5, 2), pre_kill=False)
            def _start_in_ios():
                self.bo.to_click(label='央视频')
                self.bo.wait_for_appear()

            @video2frame(video_fp)
            @record(self.plat, self.did, video_fp, offset=(1, 0))
            def _start_in_and():
                self.bo.to_click(text='央视频')
                self.bo.wait_for_appear()

            if self.plat == PLATFORM.AND:
                return _start_in_and()
            return _start_in_ios()

        before_test()
        for _ in range(repeat):
            self.bo.close_app()
            testing(splice(self.base_dir, f'cold_start_{_ + 1}.mp4'))
            time.sleep(interval)
        after_test()


if __name__ == '__main__':
    # ysp = YSPStart('android', 'TEV0217315000851', '/Users/ssfanli/Desktop/YSP_v241.apk')
    # , '/Users/ssfanli/Desktop/cctvvideo-ios_2.4.2.66007_enterprise_sign.ipa'
    ysp = YSPStart('ios', '00008110-001E54AC210A801E', '/Users/ssfanli/Desktop/cctvvideo-ios_2.4.2.66007_enterprise_sign.ipa')
    ysp.cold_start(3)


