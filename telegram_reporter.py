import asyncio
import os
import sys

from dotenv import load_dotenv
from telethon import TelegramClient, functions
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from telethon.tl.types import InputReportReasonOther

load_dotenv()

API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']
BOT_TOKEN = os.environ['BOT_TOKEN']


fuckyou_russia_channels = [
    [704120365, "https://t.me/rusfleet"],
    [640719968, "https://t.me/annavegdash"],
    [699746908, "https://t.me/milinfolive"],
    [699746908, "https://t.me/omonmoscow"],
    [699746908, "https://t.me/neoficialniybezsonov"],
    [699746908, "https://t.me/rybar"],
    [398034986, "https://t.me/dnepr_partizani"],
    [699746908, "https://t.me/vladlentatarsky"],
    [699746908, "https://t.me/russ_orientalist"],
    [618778168, "@claymoreboomsbot"],
    [618778168, "https://t.me/+vkwsajjvatsyzme6"],
    [699746908, "https://t.me/brussinf"],
    [699746908, "https://t.me/lady_north"],
    [699746908, "https://t.me/medvedevvesti"],
    [562950940, "https://t.me/+kr7bna9kjmxjmtri"],
    [699746908, "https://t.me/pezdicide"],
    [699746908, "https://t.me/hackberegini"],
    [699746908, "https://t.me/mig41"],
    [699746908, "https://t.me/chvkmedia"],
    [699746908, "https://t.me/go338"],
    [699746908, "https://t.me/grey_zone"],
    [699746908, "https://t.me/boris_rozhin"],
    [618778168, "https://t.me/claymoreair"],
    [259604407, "https://t.me/unitynationnarmyspb"],
    [2048763771, "https://t.me/voyna"],
    [2048763771, "https://t.me/soc_blog"],
    [1390880182, "@vsu_info_bot"],
    [1390880182, "https://t.me/+vkwsajjvatsyzme6"],
    [1390880182, "https://t.me/+unfi6kkvo3a3ytc6"],
    [1855097951, "https://t.me/balkanossiper"],
    [295153950, "https://t.me/c/1695595486/737"],
    [264892163, "https://t.me/bloodysx"],
    [748667424, "https://t.me/putch111/8868"],
    [238497670, "https://t.me/+unfi6kkvo3a3ytc6"],
    [337091495, "https://t.me/wtyhe237"],
    [244907043, "https://t.me/voenacher"],
    [674094006, "https://t.me/korotkoiyasn"],
    [79931143, "https://t.me/tikandelaki"],
    [418726734, "https://t.me/+hyvaiu13eew4n2yy"],
    [66662555, "https://t.me/bomsclaim"],
    [558782530, "https://t.me/superdolgov"],
    [792974613, "https://t.me/swodki"],
    [447847291, "https://t.me/znahar_f1"],
    [401054155, "https://t.me/warjournaltg"],
    [317376926, "https://t.me/bomsclaim"],
    [882366211, "https://t.me/+cxnicxswkny5y2ri"],
    [248644576, "https://t.me/gurnalistyrossii"],
    [868371077, "https://t.me/+uosbhdilzf8zodfi"],
    [698113038, "https://t.me/+jsc5acpblik2njcy"],
    [882366211, "https://t.me/+plfpyhzgs742mmm6"],
    [589891694, "@proxy_foxy"],
    [410930267, "https://t.me/intelslava"],
    [868371077, "https://t.me/+qhhh8l_x5303nmyy"],
    [295153950, "https://t.me/c/1695595486/770"],
    [907051714, "https://t.me/rusvesnasu"],
    [192769152, "https://t.me/generalnote"],
    [672624386, "@milinfolive"],
    [459213705, "https://t.me/rus_armi"],
    [244907043, "https://t.me/sil0viki"],
    [415928019, "https://t.me/+odf_lvjzbnqyywfi"],
    [373170931, "https://t.me/notes_veterans"],
    [672624386, "@boris_rozhin"],
    [312512458, "https://t.me/cbpub"],
    [504750496, "https://t.me/rlz_the_kraken"],
    [554002694, "https://t.me/freedfirefire"],
    [451583904, "https://t.me/voyna_ukraina_rosia/6883"],
    [1987152515, "https://t.me/verbaaa"],
    [386209783, "https://t.me/brosok_mangusta_z"],
    [554002694, "https://t.me/+haafbhzv7grlmzmy"],
    [1923290033, "https://t.me/zheltyeslivy"],
    [401054155, "https://t.me/+bwhcxhbu8my4yzri"],
    [386209783, "https://t.me/surf_noise1"],
    [401054155, "https://t.me/bbbreaking"],
    [459213705, "https://t.me/istorijaoruzija"],
    [552544902, "https://t.me/ukraine_news_0"],
    [1987152515, "https://t.me/verbaaa"],
    [484769170, "https://t.me/bahamov_ua"],
    [401054155, "https://t.me/ugolok_sitha"],
    [834525588, "https://t.me/chp_donetsk/9680"],
    [730121068, "https://t.me/newstt2022"],
    [882366211, "https://t.me/+k5g8o_wc4zpmntli"],
    [883413132, "https://t.me/truexanewspol"],
    [649355345, "https://t.me/strelkovii"],
    [55847097, "@go338"],
    [55847097, "@chvkmedia"],
    [1533303936, "@kievdoroga"],
    [722609862, "https://t.me/+vvbrth0qokywyzm6"],
    [55847097, "@pl_syrenka"],
    [490449472, "https://t.me/tazashonews"],
    [55847097, "@lady_north"],
    [55847097, "@usaperiodical"],
    [554002694, "https://t.me/boomsclaymore"],
    [489553460, "https://t.me/warfakes"],
    [401054155, "https://t.me/ice_inii"],
    [295153950, "https://t.me/c/1483183478/1901"],
    [178624503, "https://t.me/sonofmonarchy"],
    [55847097, "@grey_zone"],
    [351497398, "https://t.me/joinchat/r4khp-wylvoptx6u"],
    [401054155, "https://t.me/informator_life"],
    [363746651, "https://t.me/warfakeres"],
    [338704881, "https://t.me/wtyhe237/25"],
    [55847097, "@omonmoscow"],
    [401054155, "https://t.me/chesnokmedia"],
    [55847097, "@wingsofwar"],
    [401054155, "https://t.me/ghost_of_novorossia"],
    [55847097, "@hackberegini"],
    [55847097, "@mig41"],
    [55847097, "@pezdicide"],
    [225347784, "https://t.me/stremobzornews"],
    [55847097, "@sergeykolyasnikov"],
    [122128499, "https://t.me/minakhachatryan"],
    [55847097, "@medvedevvesti"],
    [401054155, "https://t.me/diplomatia"],
    [55847097, "@sil0viki"],
    [672624386, "@rybar"],
    [55847097, "@balkanossiper"],
    [672624386, "@russ_orientalist"],
    [401054155, "https://t.me/bulbe_de_trones"],
    [55847097, "@brussinf"],
    [672624386, "@vladlentatarsky"],
    [341945038, "https://t.me/claymoreairz"],
    [341945038, "https://t.me/bomsclaim"],
    [122128499, "https://t.me/mikayelbad"],
    [401054155, "https://t.me/olegtsarov"],
    [371219387, "https://t.me/wingsofwar"],
    [672624386, "@neoficialniybezsonov"],
    [587341353, "@vsu_info_bot"],
    [55847097, "@sex_drugs_kahlo"],
    [205512166, "https://t.me/akimapache"],
    [122128499, "https://t.me/armenianvendetta"],
    [401054155, "https://t.me/zola_of_renovation"],
    [401054155, "https://t.me/hard_blog_line"],
    [386209783, "https://t.me/rvvoenkor"],
    [690238130, "https://t.me/nwsru/20578"],
    [401054155, "https://t.me/infantmilitario"],
    [178624503, "https://t.me/maximyusin"],
    [1003941057, "@neoficialniybezsonov"],
    [457867867, "https://t.me/zloyrusskiy_bot"],
    [951999241, "https://t.me/+gbeusmbc4h0wntni"],
    [715175497, "https://t.me/stranaua/27157"],
    [810940238, "https://t.me/tg_tcn/12375"],
    [2127504321, "https://t.me/u_now/19620"],
    [1111174258, "https://t.me/tg_tcn"],
    [205512166, "https://t.me/annashafran"],
    [1910933338, "https://t.me/hueviyherson/8188"],
    [994422757, "https://t.me/ukraina_ru"],
    [178624503, "https://t.me/yudenich"],
    [364343690, "https://t.me/intelslav"],
    [1743962409, "https://t.me/svezhaknovost"],
    [722880105, "@militaristmail"],
    [722880105, "https://t.me/infantmilitario"],
    [372625477, "https://t.me/embajadarusaru"],
    [299478537, "https://t.me/za_derjavy"],
    [886869765, "@mst102"],
    [886869765, "@george_go"],
    [886869765, "https://t.me/fak_tu"],
    [1061349632, "https://t.me/bomsclaim"],
    [1061349632, "https://t.me/hhh6660"],
    [1061349632, "https://t.me/claymoreairz"],
    [460064693, "https://t.me/majorselivanov"],
    [514448909, "https://t.me/+kntzqxhg4ku1zdvi"],
    [630944684, "https://t.me/claymoreairz"],
    [371219387, "https://t.me/sergeykolyasnikov"],
    [423183676, "https://t.me/+urtd-bh-ttk4ntbi"],
    [437012690, "https://t.me/rian_ru"],
    [270431410, "https://t.me/+vbr4dcqqz9tkzdyy"],
    [312120710, "https://t.me/video_vibe"],
    [558594969, "https://t.me/besedaob"],
    [291758614, "https://t.me/nezhurka"],
    [205512166, "https://t.me/akitilop"],
    [676365013, "https://t.me/cuisine_by"],
    [418581031, "https://t.me/srochnow"],
    [567314824, "https://t.me/+z7egs-j2zug4ytg6"],
    [299478537, "https://t.me/beregtime"],
    [653640170, "https://t.me/wargonzo"],
    [299478537, "https://t.me/opyat22"],
    [312120710, "https://t.me/+zi26eham-0u2otji"],
    [281988722, "https://t.me/vnborodinpolitik"],
    [1743962409, "https://t.me/grivni24_bot?start=ref7101155"],
    [609926150, "https://t.me/otpervogolitsa"],
    [401054155, "https://t.me/rt_russian"],
    [468284295, "https://t.me/ok_spn"],
    [299478537, "https://t.me/st_varg"],
    [583117484, "https://t.me/zloyecolog"],
    [299478537, "https://t.me/npo_dvina"],
    [371219387, "https://t.me/pl_syrenka"],
    [360126097, "https://t.me/+4yc263orkq4zyzqy"],
    [401054155, "https://t.me/gazetaru"],
    [855401802, "https://t.me/c/1141853263/164839"],
    [299478537, "https://t.me/sev_polit_takt"],
    [421645657, "https://t.me/svoikr"],
    [371219387, "https://t.me/sex_drugs_kahlo"],
    [299478537, "https://t.me/donbassyasinovatayanaliniiognia"],
    [348778062, "https://t.me/wtyhe237"],
    [371534799, "https://t.me/montyan"],
    [299478537, "https://t.me/soldiers_truth"],
    [221922953, "@bomsclaim"],
    [299478537, "https://t.me/miroshnik_r"],
    [440467438, "@pozdnyak_perehod"],
    [884532781, "@zayavka_rabsbot"],
    [749678234, "https://t.me/voenkorkotenok"],
    [484000327, "https://t.me/olgerd_semenow"],
    [454247458, "@1337const"],
    [401054155, "https://t.me/rbc_news"],
    [994422757, "@ukraina_ru"],
    [371219387, "https://t.me/usaperiodical"],
    [3897036, "https://t.me/mtd_sound"],
    [560661132, "https://t.me/kharkovzv"],
    [581077219, "@vanyaproskuriakov"],
    [178624503, "https://t.me/radlekukh"],
    [614898111, "https://t.me/kremlin_sekret"],
    [634862159, "https://t.me/unitynationnarmy"],
    [468284295, "https://t.me/encryptedch"],
    [1075682776, "https://t.me/siloviki_chat"],
    [602392019, "https://t.me/russiazukraine"],
    [502882046, "https://t.me/oleg_blokhin"],
    [520684699, "https://t.me/ucvfx7wc3xl2xfkktbhcsllw"],
    [441927944, "https://t.me/metkiukr"],
    [1068799263, "https://t.me/swodkilugansk"],
    [382017634, "https://t.me/+r5vua2gbhvqwioci"],
    [581721481, "https://t.me/+unobbjvwkmzkzdcy"],
    [357376139, "@xgangsterx2006x"],
    [1743962409, "https://t.me/my_za_putina"],
    [530414365, "https://t.me/julia_chicherina"],
    [116888848, "https://t.me/conqueror95"],
    [360093625, "https://t.me/vchkogpu"],
    [567314824, "@tgzona18"],
    [157444, "@zloyrusskiy_bot"],
    [299478537, "https://t.me/news_forfree"],
    [382175503, "https://t.me/rkadyrov_95"],
    [839488324, "https://t.me/voynareal"],
    [1101244705, "@pushilindenis"],
    [596177615, "https://t.me/govorit_topaz"],
    [1972142421, "https://t.me/vmakeevke"],
    [116888848, "https://t.me/siloviki_belarus"],
    [401142465, "https://t.me/intuition2036"],
    [624805107, "https://t.me/vysokygovorit"],
    [368797187, "https://t.me/govorit_topaz/1118"],
    [305424905, "https://t.me/cbejak/1335"],
    [183324307, "https://t.me/+38uhy8meojc2zgyy"],
    [134537674, "https://t.me/seryy_krot"],
    [1945079763, "https://t.me/fake_war_tg"],
    [894153321, "https://t.me/extra_vaganza"],
    [183324307, "https://t.me/c/1683135163/680"],
    [275738216, "https://t.me/+t-maftr8xevhzgu6"],
    [1943205119, "https://t.me/russian_osint"],
    [456209339, "https://t.me/peach_blossombazi"],
    [602392019, "https://t.me/russianukrainenewss"],
    [803294582, "https://t.me/anfisavist"],
    [382937842, "https://t.me/filmy_netfli"],
    [368797187, "https://t.me/czartv/2262"],
    [637177850, "https://t.me/turan_express"],
    [364343690, "https://t.me/chp_irkutsk"],
    [364343690, "https://t.me/belvestnik"],
    [634862159, "https://t.me/sputnikipogrom"],
    [634862159, "https://t.me/czartv"],
    [298410859, "https://t.me/real_cultras"],
    [364343690, "https://t.me/panteri_panteri"],
    [332229948, "https://t.me/bloknot_rossii"],
    [5128555896, "https://t.me/russianwaruk"],
    [492363283, "https://t.me/donbass_segodnya"],
    [299478537, "https://t.me/rusyerevantoday"],
    [364343690, "https://t.me/russkievperedi"],
    [634862159, "https://t.me/iskra_press"],
    [634862159, "https://t.me/podled"],
    [634862159, "https://t.me/chernaya100"],
    [634862159, "https://t.me/wargonzo"],
    [364343690, "https://t.me/vasyunin"],
    [1330955994, "https://t.me/chp_donetsk"],
    [364343690, "https://t.me/bunkerdayly"],
    [765933165, "https://t.me/+g-wjv1gzbe0xmzq6"],
    [826418607, "@notapasserby"],
    [364343690, "https://t.me/imashevnb"],
    [377284332, "https://t.me/chdambiev"],
    [379290029, "https://t.me/margaritasimonyan"],
    [364343690, "https://t.me/podled"],
    [5046682464, "https://t.me/+cnyvb4w_dwa4mtgy"],
    [530414365, "https://t.me/vedomosti"],
    [530414365, "https://t.me/tass_agency"],
    [1498035036, "https://t.me/zhestvoinaukraina"],
    [105119107, "https://t.me/minpravda"],
    [530414365, "https://t.me/kremlinprachka"],
    [634042774, "https://t.me/+plfpyhzgs742mmm6"],
    [634042774, "https://t.me/+plfpyhzgs742mmm6"],
    [634042774, "https://t.me/+plfpyhzgs742mmm6"],
    [364343690, "https://t.me/sturmang"],
    [299478537, "https://t.me/minzdravny"],
    [378321191, "@siloviki_chat"],
    [615893951, "https://t.me/pushilindenis"],
    [876498695, "@ssleg"],
    [876498695, "https://t.me/vsu_info_bot"]
]


async def main():
    client = TelegramClient(StringSession(""), API_ID, API_HASH)
    try:
        if not client.is_connected():
            await client.connect()
        if client.is_connected():
            if not await client.is_user_authorized():
                await client.sign_in(phone=input("Please, enter your telephone number: "))
                print("\n")
                try:
                    await client.sign_in(code=input("Please, enter code confirmation: "))
                    print("\n")
                except SessionPasswordNeededError:
                    await client.sign_in(password=input("Please, enter password confirmation: "))
                    print("\n")
            for channel in fuckyou_russia_channels:
                ch_id, ch_name = channel
                try:
                    result = await client(functions.messages.ReportRequest(
                        peer=ch_name,
                        id=[ch_id],
                        reason=InputReportReasonOther(),
                        message='Please, block this chat, it spreads violence and supports terrorists on Ukraine territory. '
                                'Block it to save lives in my country !! '
                    ))
                    if result:
                        print(f"Successfully reported about {ch_name}")
                except Exception as ex:
                    print(f"Failed during report about {ch_name}:\n{ex}", file=sys.stderr)
                await asyncio.sleep(3)
    except Exception as ex:
        print(f"ex is {ex}", file=sys.stderr)


if __name__ == '__main__':
    asyncio.run(main())
