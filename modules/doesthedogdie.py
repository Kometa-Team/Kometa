import requests
import json
from modules import util
logger = util.logger

class DogDieChecker:

    topics = [
        {"id":153,"category_id":2,"label":"a dog dies","does_name":"Does the dog die","slug":"does-the-dog-die"},
        {"id":319,"category_id":2,"label":"animals were harmed in the making","does_name":"Were animals harmed in the making","slug":"were-animals-harmed-in-the-making"},
        {"id":189,"category_id":2,"label":"an animal dies","does_name":"Does an animal die","slug":"does-an-animal-die"},
        {"id":229,"category_id":2,"label":"animals are abused","does_name":"Are animals abused","slug":"are-animals-abused"},
        {"id":231,"category_id":2,"label":"there's dog fighting","does_name":"Is there dog fighting","slug":"is-there-dog-fighting"},
        {"id":252,"category_id":2,"label":"there's a dead animal","does_name":"Is there a dead animal","slug":"is-there-a-dead-animal"},
        {"id":355,"category_id":2,"label":"an animal is sad","does_name":"Is an animal sad","slug":"is-an-animal-sad"},
        {"id":338,"category_id":2,"label":"rabbits are harmed","does_name":"Are rabbits harmed","slug":"are-rabbits-harmed"},
        {"id":186,"category_id":2,"label":"a cat dies","does_name":"Does a cat die","slug":"does-a-cat-die"},
        {"id":285,"category_id":2,"label":"a pet dies","does_name":"Does a pet die","slug":"does-a-pet-die"},
        {"id":196,"category_id":2,"label":"a dragon dies","does_name":"Does a dragon die","slug":"does-a-dragon-die"},
        {"id":165,"category_id":2,"label":"there are spiders","does_name":"Are there spiders","slug":"are-there-spiders"},
        {"id":332,"category_id":2,"label":"there's an alligator/crocodile","does_name":"Are there alligators/crocodiles?","slug":"are-there-alligators-crocodiles"},
        {"id":214,"category_id":2,"label":"there are snakes","does_name":"Are there snakes","slug":"are-there-snakes"},
        {"id":337,"category_id":2,"label":"there are sharks","does_name":"Are there sharks","slug":"are-there-sharks"},
        {"id":213,"category_id":2,"label":"there are bugs","does_name":"Are there bugs","slug":"are-there-bugs"},
        {"id":183,"category_id":2,"label":"a horse dies","does_name":"Does a horse die","slug":"does-a-horse-die"},
        {"id":293,"category_id":33,"label":"a child is abandoned by a parent","does_name":"Is a child abandoned by a parent","slug":"is-a-child-abandoned-by-a-parent"},
        {"id":350,"category_id":33,"label":"an animal is abandoned","does_name":"Is an animal abandoned","slug":"is-an-animal-abandoned"},
        {"id":363,"category_id":33,"label":"someone leaves without saying goodbye","does_name":"Does someone leave without saying goodbye","slug":"does-someone-leave-without-saying-goodbye"},
        {"id":242,"category_id":25,"label":"someone is stalked","does_name":"Is someone stalked","slug":"is-someone-stalked"},
        {"id":347,"category_id":25,"label":"the abused forgives their abuser","does_name":"Does an abused person forgive their abuser","slug":"does-an-abused-person-forgive-their-abuser"},
        {"id":304,"category_id":25,"label":"the abused becomes the abuser","does_name":"Does the abused become the abuser","slug":"does-the-abused-become-the-abuser"},
        {"id":237,"category_id":25,"label":"someone gets gaslighted","does_name":"Is someone gaslighted","slug":"is-someone-gaslighted"},
        {"id":365,"category_id":25,"label":"someone is abused with a belt","does_name":"Is someone abused with a belt","slug":"is-someone-abused-with-a-belt"},
        {"id":218,"category_id":25,"label":"there's child abuse","does_name":"Is a child abused","slug":"is-a-child-abused"},
        {"id":367,"category_id":25,"label":"a woman is brutalized for spectacle","does_name":"Is a woman brutalized for spectacle","slug":"is-a-woman-brutalized-for-spectacle"},
        {"id":219,"category_id":25,"label":"there's domestic violence","does_name":"Is there domestic violence","slug":"is-there-domestic-violence"},
        {"id":330,"category_id":25,"label":"there's abusive parents","does_name":"Are there abusive parents","slug":"are-there-abusive-parents"},
        {"id":225,"category_id":1,"label":"alcohol abuse","does_name":"Does someone abuse alcohol","slug":"does-someone-abuse-alcohol"},
        {"id":230,"category_id":1,"label":"there's addiction","does_name":"Is there addiction","slug":"is-there-addiction"},
        {"id":193,"category_id":1,"label":"someone uses drugs","does_name":"Does someone use drugs","slug":"does-someone-use-drugs"},
        {"id":320,"category_id":28,"label":"there's pedophilia","does_name":"Is there pedophilia","slug":"is-there-pedophilia"},
        {"id":308,"category_id":28,"label":"someone is held under water","does_name":"Is someone held under water","slug":"is-someone-held-under-water"},
        {"id":326,"category_id":28,"label":"rape is mentioned","does_name":"Is rape mentioned","slug":"is-rape-mentioned"},
        {"id":321,"category_id":28,"label":"someone is beaten up by a bully","does_name":"Is someone beaten up by a bully","slug":"is-someone-beaten-up-by-a-bully"},
        {"id":274,"category_id":28,"label":"someone is restrained","does_name":"Is someone restrained","slug":"is-someone-restrained"},
        {"id":182,"category_id":28,"label":"someone is sexually assaulted","does_name":"Is someone sexually assaulted","slug":"is-someone-sexually-assaulted"},
        {"id":360,"category_id":28,"label":"someone's mouth is covered","does_name":"Is someone's mouth covered","slug":"is-someones-mouth-covered"},
        {"id":315,"category_id":28,"label":"sexual assault on men is a joke","does_name":"Are there jokes about sexual assault on men","slug":"are-there-jokes-about-sexual-assault-on-men"},
        {"id":292,"category_id":28,"label":"someone is raped onscreen","does_name":"Is someone raped onscreen","slug":"is-someone-raped-onscreen"},
        {"id":342,"category_id":28,"label":"a woman gets slapped","does_name":"Does a woman get slapped","slug":"does-a-woman-get-slapped"},
        {"id":299,"category_id":28,"label":"someone is drugged","does_name":"Is someone drugged","slug":"is-someone-drugged"},
        {"id":352,"category_id":3,"label":"hands are damaged","does_name":"Are any hands damaged","slug":"are-any-hands-damaged"},
        {"id":362,"category_id":3,"label":"someone dislocates something","does_name":"Are there dislocations","slug":"are-there-dislocations"},
        {"id":361,"category_id":3,"label":"someone's throat is mutilated","does_name":"Is there throat mutilation","slug":"is-there-throat-mutilation"},
        {"id":245,"category_id":3,"label":"someone struggles to breathe","does_name":"Does someone struggle to breathe","slug":"does-someone-struggle-to-breathe"},
        {"id":331,"category_id":3,"label":"there's decapitation","does_name":"Is there decapitation","slug":"is-there-decapitation"},
        {"id":254,"category_id":3,"label":"there's cannibalism","does_name":"Is there cannibalism","slug":"is-there-cannibalism"},
        {"id":282,"category_id":3,"label":"someone is crushed to death","does_name":"Is someone crushed to death","slug":"is-someone-crushed-to-death"},
        {"id":309,"category_id":3,"label":"somebody is choked","does_name":"Is someone choked","slug":"is-someone-choked"},
        {"id":164,"category_id":3,"label":"someone is burned alive","does_name":"Is someone burned alive","slug":"is-someone-burned-alive"},
        {"id":240,"category_id":3,"label":"someone is buried alive","does_name":"Is someone buried alive","slug":"is-someone-buried-alive"},
        {"id":296,"category_id":3,"label":"there's body horror","does_name":"Is there body horror","slug":"is-there-body-horror"},
        {"id":250,"category_id":3,"label":"there's amputation","does_name":"Is there amputation","slug":"is-there-amputation"},
        {"id":223,"category_id":3,"label":"heads get squashed","does_name":"Does a head get squashed","slug":"does-a-head-get-squashed"},
        {"id":280,"category_id":3,"label":"there's Achilles Tendon injury","does_name":"Is there Achilles Tendon injury","slug":"is-there-achilles-tendon-injury"},
        {"id":177,"category_id":3,"label":"there's shaving/cutting","does_name":"Is there shaving/cutting","slug":"is-there-shaving-cutting"},
        {"id":281,"category_id":3,"label":"someone asphyxiates","does_name":"Does someone asphyxiate","slug":"does-someone-asphyxiate"},
        {"id":210,"category_id":3,"label":"teeth are damaged","does_name":"Are any teeth damaged","slug":"are-any-teeth-damaged"},
        {"id":298,"category_id":3,"label":"Someone becomes unconscious","does_name":"Does someone become unconscious","slug":"does-someone-become-unconscious"},
        {"id":216,"category_id":3,"label":"someone breaks a bone","does_name":"Does someone break a bone","slug":"does-someone-break-a-bone"},
        {"id":206,"category_id":3,"label":"somone has a seizure","does_name":"Does someone have a seizure","slug":"does-someone-have-a-seizure"},
        {"id":258,"category_id":3,"label":"there's genital trauma/mutilation","does_name":"Is there genital trauma/mutilation","slug":"is-there-genital-trauma-mutilation"},
        {"id":171,"category_id":3,"label":"there's finger/toe mutilation","does_name":"Is there finger/toe mutilation","slug":"is-there-finger-toe-mutilation"},
        {"id":203,"category_id":3,"label":"there's torture","does_name":"Is someone tortured","slug":"is-someone-tortured"},
        {"id":271,"category_id":3,"label":"someone falls down stairs","does_name":"Does someone fall down stairs","slug":"does-someone-fall-down-stairs"},
        {"id":211,"category_id":3,"label":"someone falls to their death","does_name":"Does someone fall to their death","slug":"does-someone-fall-to-their-death"},
        {"id":200,"category_id":3,"label":"there's eye mutilation","does_name":"Is there eye mutilation","slug":"is-there-eye-mutilation"},
        {"id":343,"category_id":3,"label":"someone is stabbed","does_name":"Is someone stabbed","slug":"is-someone-stabbed"},
        {"id":267,"category_id":3,"label":"there's excessive gore","does_name":"Is there excessive gore","slug":"is-there-excessive-gore"},
        {"id":227,"category_id":3,"label":"there are hangings","does_name":"Is there a hanging","slug":"is-there-a-hanging"},
        {"id":284,"category_id":23,"label":"an infant is abducted","does_name":"Is an infant abducted","slug":"is-an-infant-abducted"},
        {"id":287,"category_id":23,"label":"a minor is sexualized","does_name":"Is a minor sexualized","slug":"is-a-minor-sexualized"},
        {"id":158,"category_id":23,"label":"a kid dies","does_name":"Does a kid die","slug":"does-a-kid-die"},
        {"id":357,"category_id":26,"label":"there's bedbugs","does_name":"Are there bedbugs","slug":"are-there-bedbugs"},
        {"id":289,"category_id":22,"label":"someone sacrifices themselves","does_name":"Does someone sacrifice themselves","slug":"does-someone-sacrifice-themselves"},
        {"id":305,"category_id":22,"label":"a non-human character dies","does_name":"Does a non-human character die","slug":"does-a-non-human-character-die"},
        {"id":311,"category_id":22,"label":"someone dies","does_name":"Does someone die","slug":"does-someone-die"},
        {"id":328,"category_id":22,"label":"a major character dies","does_name":"Does a major character die","slug":"does-a-major-character-die"},
        {"id":272,"category_id":27,"label":"the r-slur is used","does_name":"Is the r-slur used","slug":"is-the-r-slur-used"},
        {"id":353,"category_id":27,"label":"someone disabled played by able-bodied","does_name":"Is someone disabled played by able-bodied","slug":"is-someone-disabled-played-by-able-bodied"},
        {"id":275,"category_id":21,"label":"someone overdoses","does_name":"Does someone overdose","slug":"does-someone-overdose"},
        {"id":168,"category_id":4,"label":"a parent dies","does_name":"Does a parent die","slug":"does-a-parent-die"},
        {"id":241,"category_id":4,"label":"someone cheats","does_name":"Does someone cheat","slug":"does-someone-cheat"},
        {"id":253,"category_id":4,"label":"A child's dear toy is destroyed","does_name":"Is a child's toy destroyed","slug":"is-a-childs-toy-destroyed"},
        {"id":243,"category_id":4,"label":"someone is kidnapped","does_name":"Is someone kidnapped","slug":"is-someone-kidnapped"},
        {"id":313,"category_id":4,"label":"a family member dies","does_name":"Does a family member die","slug":"does-a-family-member-die"},
        {"id":161,"category_id":10,"label":"there are jumpscares","does_name":"Are there jumpscares","slug":"are-there-jumpscares"},
        {"id":224,"category_id":10,"label":"someone is possessed","does_name":"Is someone possessed","slug":"is-someone-possessed"},
        {"id":207,"category_id":10,"label":"there's ghosts","does_name":"Are there ghosts","slug":"are-there-ghosts"},
        {"id":174,"category_id":10,"label":"there are clowns","does_name":"Are there clowns","slug":"are-there-clowns"},
        {"id":335,"category_id":10,"label":"there's natural bodies of water","does_name":"Are there natural bodies of water","slug":"are-there-natural-bodies-of-water"},
        {"id":312,"category_id":10,"label":"trypophobic content is shown","does_name":"Is trypophobic content shown","slug":"is-trypophobic-content-shown"},
        {"id":297,"category_id":10,"label":"there are razors","does_name":"Are there razors","slug":"are-there-razors"},
        {"id":176,"category_id":10,"label":"there are shower scenes","does_name":"Is there a shower scene","slug":"is-there-a-shower-scene"},
        {"id":295,"category_id":10,"label":"there are mannequins","does_name":"Are there mannequins","slug":"are-there-mannequins"},
        {"id":257,"category_id":5,"label":"someone wets/soils themselves","does_name":"Does someone wet/soil themselves","slug":"does-someone-wet-soil-themselves"},
        {"id":201,"category_id":5,"label":"someone vomits","does_name":"Does someone vomit","slug":"does-someone-vomit"},
        {"id":322,"category_id":5,"label":"someone is eaten","does_name":"Is someone eaten","slug":"is-someone-eaten"},
        {"id":354,"category_id":5,"label":"someone poops on-screen","does_name":"Is there on-screen pooping","slug":"is-there-on-screen-pooping"},
        {"id":180,"category_id":5,"label":"there's spitting","does_name":"Does someone spit","slug":"does-someone-spit"},
        {"id":255,"category_id":5,"label":"There's audio gore","does_name":"Is there audio gore","slug":"is-there-audio-gore"},
        {"id":324,"category_id":5,"label":"there's farting","does_name":"Is there farting","slug":"is-there-farting"},
        {"id":283,"category_id":46,"label":"there are 9/11 depictions","does_name":"Are there 9/11 depictions","slug":"are-there-9-11-depictions"},
        {"id":256,"category_id":40,"label":"there is copaganda","does_name":"Is there copaganda","slug":"is-there-copaganda"},
        {"id":345,"category_id":40,"label":"there's incarceration","does_name":"Is there incarceration","slug":"is-there-incarceration"},
        {"id":314,"category_id":19,"label":"there are transphobic slurs","does_name":"Are there transphobic slurs","slug":"are-there-transphobic-slurs"},
        {"id":359,"category_id":19,"label":"a trans person is depicted predatorily","does_name":"Is a trans person depicted predatorily","slug":"is-a-trans-person-depicted-predatorily"},
        {"id":301,"category_id":19,"label":"there's bisexual cheating","does_name":"Is there bisexual cheating","slug":"is-there-bisexual-cheating"},
        {"id":310,"category_id":19,"label":"there's deadnaming or birthnaming","does_name":"Is there deadnaming or birthnaming","slug":"is-there-deadnaming-or-birthnaming"},
        {"id":368,"category_id":19,"label":"an LGBT+ person is outed","does_name":"Is an LGBT+ person outed","slug":"is-an-lgbt-person-outed"},
        {"id":329,"category_id":37,"label":"a priceless artifact is destroyed","does_name":"Is a priceless artifact destroyed","slug":"is-a-priceless-artifact-destroyed"},
        {"id":190,"category_id":6,"label":"needles/syringes are used","does_name":"Are needles/syringes used","slug":"are-needles-syringes-used"},
        {"id":205,"category_id":6,"label":"electro-therapy is used","does_name":"Is electro-therapy used","slug":"is-electro-therapy-used"},
        {"id":192,"category_id":6,"label":"there's a hospital scene","does_name":"Is there a hospital scene","slug":"is-there-a-hospital-scene"},
        {"id":358,"category_id":6,"label":"there's menstruation","does_name":"Is there menstruation","slug":"is-there-menstruation"},
        {"id":204,"category_id":6,"label":"someone has cancer","does_name":"Does someone have cancer","slug":"does-someone-have-cancer"},
        {"id":220,"category_id":6,"label":"there's a mental institution scene","does_name":"Is there a mental institution scene","slug":"is-there-a-mental-institution-scene"},
        {"id":336,"category_id":7,"label":"someone has a mental illness","does_name":"Does someone have a mental illness","slug":"does-someone-have-a-mental-illness"},
        {"id":199,"category_id":7,"label":"someone self harms","does_name":"Does someone self harm","slug":"does-someone-self-harm"},
        {"id":349,"category_id":7,"label":"autism is misrepresented","does_name":"Is autism misrepresented","slug":"is-autism-misrepresented"},
        {"id":263,"category_id":7,"label":"a mentally ill person is violent","does_name":"Is a mentally ill person violent","slug":"is-a-mentally-ill-person-violent"},
        {"id":370,"category_id":7,"label":"there's dissociation, depersonalization, or derealization","does_name":"Is there dissociation, depersonalization, or derealization","slug":"is-there-dissociation-depersonalization-or-derealization"},
        {"id":302,"category_id":7,"label":"D.I.D. Misrepresentation","does_name":"Is there D.I.D. misrepresentation","slug":"is-there-d-i-d-misrepresentation"},
        {"id":286,"category_id":7,"label":"Someone attempts suicide","does_name":"Does someone attempt suicide","slug":"does-someone-attempt-suicide"},
        {"id":334,"category_id":7,"label":"reality is unstable or unhinged","does_name":"Is reality unstable or unhinged","slug":"is-reality-unstable-or-unhinged"},
        {"id":265,"category_id":7,"label":"someone suffers from PTSD","does_name":"Does someone suffer from PTSD","slug":"does-someone-suffer-from-ptsd"},
        {"id":260,"category_id":7,"label":"there's misophonia","does_name":"Is there misophonia","slug":"is-there-misophonia"},
        {"id":323,"category_id":7,"label":"there's ABA therapy","does_name":"Is there ABA therapy","slug":"is-there-aba-therapy"},
        {"id":306,"category_id":7,"label":"there's body dysphoria","does_name":"Is there body dysphoria","slug":"is-there-body-dysphoria"},
        {"id":195,"category_id":7,"label":"there's body dysmorphia","does_name":"Is there body dysmorphia","slug":"is-there-body-dysmorphia"},
        {"id":259,"category_id":7,"label":"someone says \"I'll kill myself\"","does_name":"Does someone say \"I'll kill myself\"","slug":"does-someone-say-ill-kill-myself"},
        {"id":235,"category_id":7,"label":"someone has an anxiety attack","does_name":"Are there anxiety attacks","slug":"are-there-anxiety-attacks"},
        {"id":202,"category_id":7,"label":"there's a claustrophobic scene","does_name":"Is there a claustrophobic scene","slug":"is-there-a-claustrophobic-scene"},
        {"id":217,"category_id":7,"label":"someone has an eating disorder","does_name":"Does someone have an eating disorder","slug":"does-someone-have-an-eating-disorder"},
        {"id":248,"category_id":7,"label":"Autism specific abuse","does_name":"Is there autism specific abuse","slug":"is-there-autism-specific-abuse"},
        {"id":187,"category_id":7,"label":"someone dies by suicide","does_name":"Does someone die by suicide","slug":"does-someone-die-by-suicide"},
        {"id":348,"category_id":7,"label":"someone has a meltdown","does_name":"Does someone have a meltdown","slug":"does-someone-have-a-meltdown"},
        {"id":339,"category_id":8,"label":"there are sudden loud noises","does_name":"Are there sudden loud noises","slug":"are-there-sudden-loud-noises"},
        {"id":356,"category_id":8,"label":"there's underwater scenes","does_name":"Are there underwater scenes","slug":"are-there-underwater-scenes"},
        {"id":261,"category_id":8,"label":"a baby cries","does_name":"Does a baby cry","slug":"does-a-baby-cry"},
        {"id":181,"category_id":8,"label":"shaky cam is used","does_name":"Is there shakey cam","slug":"is-there-shakey-cam"},
        {"id":366,"category_id":8,"label":"there's screaming","does_name":"Is there screaming","slug":"is-there-screaming"},
        {"id":290,"category_id":8,"label":"there is obscene language/gestures","does_name":"Is there obscene language/gestures","slug":"is-there-obscene-language-gestures"},
        {"id":167,"category_id":8,"label":"there's flashing lights or images","does_name":"Are there flashing lights or images","slug":"are-there-flashing-lights-or-images"},
        {"id":318,"category_id":18,"label":"someone is watched without knowing","does_name":"Is someone watched without knowing","slug":"is-someone-watched-without-knowing"},
        {"id":268,"category_id":18,"label":"the fourth wall is broken","does_name":"Is the fourth wall broken","slug":"is-the-fourth-wall-broken"},
        {"id":264,"category_id":9,"label":"a baby is stillborn","does_name":"Is a baby stillborn","slug":"is-a-baby-stillborn"},
        {"id":228,"category_id":9,"label":"there's childbirth","does_name":"Is there childbirth","slug":"is-there-childbirth"},
        {"id":238,"category_id":9,"label":"someone has an abortion","does_name":"Are there abortions","slug":"are-there-abortions"},
        {"id":266,"category_id":9,"label":"there is a baby or unborn child","does_name":"Are there babies or unborn children","slug":"are-there-babies-or-unborn-children"},
        {"id":215,"category_id":9,"label":"someone miscarries","does_name":"Does someone miscarry","slug":"does-someone-miscarry"},
        {"id":239,"category_id":9,"label":"a pregnant person dies","does_name":"Does a pregnant person die","slug":"does-a-pregnant-person-die"},
        {"id":233,"category_id":45,"label":"there's fat jokes","does_name":"Are there fat jokes","slug":"are-there-fat-jokes"},
        {"id":226,"category_id":45,"label":"someone is misgendered","does_name":"Is someone misgendered","slug":"is-someone-misgendered"},
        {"id":247,"category_id":45,"label":"there are homophobic slurs","does_name":"Are there homophobic slurs","slug":"are-there-homophobic-slurs"},
        {"id":246,"category_id":45,"label":"there's antisemitism","does_name":"Is there antisemitism","slug":"is-there-antisemitism"},
        {"id":262,"category_id":45,"label":"there are \"Man in a dress\" jokes","does_name":"Are there \"Man in a dress\" jokes","slug":"are-there-man-in-a-dress-jokes"},
        {"id":212,"category_id":45,"label":"someone speaks hate speech","does_name":"Is there hate speech","slug":"is-there-hate-speech"},
        {"id":294,"category_id":45,"label":"a minority is misrepresented","does_name":"Is a minority is misrepresented","slug":"is-a-minority-is-misrepresented"},
        {"id":194,"category_id":45,"label":"an LGBT person dies","does_name":"Does an LGBT person die","slug":"does-an-lgbt-person-die"},
        {"id":234,"category_id":45,"label":"the black guy dies first","does_name":"Does the black guy die first","slug":"does-the-black-guy-die-first"},
        {"id":251,"category_id":45,"label":"someone says the n-word","does_name":"Are there n-words","slug":"are-there-n-words"},
        {"id":303,"category_id":45,"label":"there's aphobia","does_name":"Is there aphobia","slug":"is-there-aphobia"},
        {"id":244,"category_id":45,"label":"there's ableist language or behavior","does_name":"Is there ableist language or behavior","slug":"is-there-ableist-language-or-behavior"},
        {"id":325,"category_id":24,"label":"there's blackface","does_name":"Is there blackface","slug":"is-there-blackface"},
        {"id":277,"category_id":41,"label":"there's a large age gap","does_name":"Is there a large age gap","slug":"is-there-a-large-age-gap"},
        {"id":351,"category_id":30,"label":"religion is discussed","does_name":"Is religion discussed","slug":"is-religion-discussed"},
        {"id":369,"category_id":30,"label":"there's demons or Hell","does_name":"Are there demons or Hell","slug":"are-there-demons-or-hell"},
        {"id":197,"category_id":11,"label":"there is sexual content","does_name":"Is there sexual content","slug":"is-there-sexual-content"},
        {"id":276,"category_id":11,"label":"someone is sexually objectified","does_name":"Is someone sexually objectified","slug":"is-someone-sexually-objectified"},
        {"id":279,"category_id":11,"label":"there are nude scenes","does_name":"Are there nude scenes","slug":"are-there-nude-scenes"},
        {"id":307,"category_id":11,"label":"there's bestiality","does_name":"Is there bestiality","slug":"is-there-bestiality"},
        {"id":364,"category_id":11,"label":"there's BDSM","does_name":"Is there BDSM","slug":"is-there-bdsm"},
        {"id":317,"category_id":11,"label":"someone loses their virginity","does_name":"Does someone lose their virginity","slug":"does-someone-lose-their-virginity"},
        {"id":236,"category_id":11,"label":"there are incestuous relationships","does_name":"Are there incestuous relationships","slug":"are-there-incestuous-relationships"},
        {"id":273,"category_id":44,"label":"a male character is ridiculed for crying","does_name":"Is a male character ridiculed for crying","slug":"is-a-male-character-ridiculed-for-crying"},
        {"id":288,"category_id":29,"label":"someone has a chronic illness","does_name":"Does someone have a chronic illness","slug":"does-someone-have-a-chronic-illness"},
        {"id":291,"category_id":29,"label":"someone has dementia/Alzheimer's","does_name":"Is there dementia/Alzheimer's","slug":"is-there-dementia-alzheimers"},
        {"id":327,"category_id":29,"label":"someone is terminally ill","does_name":"Is someone terminally ill","slug":"is-someone-terminally-ill"},
        {"id":278,"category_id":29,"label":"someone has a stroke","does_name":"Does someone have a stroke","slug":"does-someone-have-a-stroke"},
        {"id":270,"category_id":12,"label":"someone is homeless","does_name":"Is someone homeless","slug":"is-someone-homeless"},
        {"id":316,"category_id":12,"label":"there's anti-abortion themes","does_name":"Are there anti-abortion themes","slug":"are-there-anti-abortion-themes"},
        {"id":300,"category_id":12,"label":"there's fat suits","does_name":"Are there fat suits","slug":"are-there-fat-suits"},
        {"id":341,"category_id":12,"label":"existentialism is debated","does_name":"Is existentialism debated","slug":"is-existentialism-debated"},
        {"id":209,"category_id":13,"label":"Santa (et al) is spoiled","does_name":"Is Santa (et al) spoiled","slug":"is-santa-et-al-spoiled"},
        {"id":346,"category_id":13,"label":"there's end credits scenes?","does_name":"Are there end credit scenes","slug":"are-there-end-credit-scenes"},
        {"id":222,"category_id":13,"label":"the ending is sad","does_name":"Does it have a sad ending","slug":"does-it-have-a-sad-ending"},
        {"id":184,"category_id":17,"label":"a car crashes","does_name":"Does a car crash","slug":"does-a-car-crash"},
        {"id":269,"category_id":17,"label":"a car honks or tires screech","does_name":"Does a car honk or tires screech","slug":"does-a-car-honk-or-tires-screech"},
        {"id":198,"category_id":17,"label":"a plane crashes","does_name":"Does a plane crash","slug":"does-a-plane-crash"},
        {"id":208,"category_id":17,"label":"a person is hit by a car","does_name":"Is someone hit by a car","slug":"is-someone-hit-by-a-car"},
        {"id":221,"category_id":14,"label":"there's a nuclear explosion","does_name":"Is there a nuclear explosion","slug":"is-there-a-nuclear-explosion"},
        {"id":188,"category_id":14,"label":"there's blood/gore","does_name":"Is there blood/gore","slug":"is-there-blood-gore"},
        {"id":191,"category_id":14,"label":"someone drowns","does_name":"Does someone drown","slug":"does-someone-drown"},
        {"id":232,"category_id":14,"label":"there's gun violence","does_name":"Is there gun violence","slug":"is-there-gun-violence"},
    ]

    categories = [
        {"name":"Animal","id":2},
        {"name":"Abandonment","id":33},
        {"name":"Abuse","id":25},
        {"name":"Addiction","id":1},
        {"name":"Assault","id":28},
        {"name":"Bodily Harm","id":3},
        {"name":"Children","id":23},
        {"name":"Creepy Crawly","id":26},
        {"name":"Death","id":22},
        {"name":"Disability","id":27},
        {"name":"Drugs/Alcohol","id":21},
        {"name":"Family","id":4},
        {"name":"Fear","id":10},
        {"name":"Gross","id":5},
        {"name":"Large-scale Violence","id":46},
        {"name":"Law Enforcement","id":40},
        {"name":"LGBTQ+","id":19},
        {"name":"Loss","id":37},
        {"name":"Medical","id":6},
        {"name":"Mental Health","id":7},
        {"name":"Noxious","id":8},
        {"name":"Paranoia","id":18},
        {"name":"Pregnancy","id":9},
        {"name":"Prejudice","id":45},
        {"name":"Race","id":24},
        {"name":"Relationships","id":41},
        {"name":"Religious","id":30},
        {"name":"Sex","id":11},
        {"name":"Sexism","id":44},
        {"name":"Sickness","id":29},
        {"name":"Social","id":12},
        {"name":"Spoiler","id":13},
        {"name":"Vehicular","id":17},
        {"name":"Violence","id":14},
    ]
    
    topic_map = {topic['slug']: topic for topic in topics}
    category_map = {category['name']: category for category in categories}
    
    def __init__(self, config, api_key):
        self.dtdd_api_key = api_key
        self.config = config
        self.api_headers = {'Accept': 'application/json', 'X-API-KEY': self.dtdd_api_key}
        self.base_search_url = "https://www.doesthedogdie.com/dddsearch"
        self.base_media_url = "https://www.doesthedogdie.com/media"

    @classmethod
    def get_topic_id_by_slug(cls, slug):
        topic = cls.topic_map.get(slug)
        if topic:
            return topic["id"]
        else:
            return None

    @classmethod
    def get_all_labels(cls):
        return [' '.join([word.capitalize() for word in topic["label"].split()]) for topic in cls.topics]

    @classmethod
    def get_all_topic_ids(cls):
        return [topic["id"] for topic in cls.topics]
    
    @classmethod
    def get_category_id_by_name(cls, name):
        lowercase_name = name.lower()
        for category_name, category in cls.category_map.items():
            if category_name.lower() == lowercase_name:
                return category["id"]
        return None
        
    @classmethod
    def get_topic_ids_by_category_id(cls, category_id):
        return [topic["id"] for topic in cls.topics if topic["category_id"] == category_id]
        
    def _get_response(self, url, params=None):
        response = requests.get(url, params=params, headers=self.api_headers)
        return response

    def search_movie(self, movie_name, year=None, topic_ids=[]):
        search_params = {'q': movie_name}
        if year:
            search_params['year'] = year
        response = self._get_response(self.base_search_url, params=search_params)
        if response.status_code == 200:
            search_results = response.json()
            movie_id = self._extract_movie_id(search_results, movie_name, year)
            if movie_id:
                movie_info = self._get_movie_info(movie_id)
                topic_labels = self._get_topic_labels(movie_info, topic_ids)
                return topic_labels
        return []

    def _extract_movie_id(self, search_results, movie_name, year=None):
        filtered_results = [result for result in search_results.get('items', []) if result.get('name').lower() == movie_name.lower()]
        if year:
            filtered_results = [result for result in filtered_results if str(result.get('releaseYear')) == str(year)]
        if filtered_results:
            return filtered_results[0].get('id')
        elif search_results.get('items'):
            # If no exact match found for the year, return the ID of the first item
            return search_results['items'][0].get('id')
        return None

    def _get_movie_info(self, movie_id):
        movie_url = f"{self.base_media_url}/{movie_id}"
        response = self._get_response(movie_url)
        if response.status_code == 200:
            movie_info = response.json()
            return movie_info
        return None

    def _get_topic_labels(self, movie_info, topic_ids=None):
        topic_labels = []
        topic_stats = movie_info.get('topicItemStats', [])
        for topic_stat in topic_stats:
            topic_id = topic_stat.get('topic', {}).get('id')
            if not topic_ids or topic_id in topic_ids:
                yes_sum = topic_stat.get('yesSum')
                no_sum = topic_stat.get('noSum')
                is_yes = yes_sum > no_sum
                if is_yes:
                    topic_name = topic_stat.get('topic', {}).get('name')
                    topic_label = ' '.join([word.capitalize() for word in topic_name.split()])
                    topic_labels.append(topic_label)
        return topic_labels

    def _get_topic_stats(self, movie_info):
        topic_stats = {}
        for topic_stat in movie_info.get('topicItemStats', []):
            topic_id = topic_stat.get('topic', {}).get('id')
            yes_sum = topic_stat.get('yesSum')
            no_sum = topic_stat.get('noSum')
            is_yes = yes_sum > no_sum
            topic_stats[topic_id] = is_yes
        return topic_stats

    def _get_topic_name(self, movie_info, topic_id):
        for topic_stat in movie_info.get('topicItemStats', []):
            if topic_stat.get('topic', {}).get('id') == topic_id:
                return topic_stat.get('topic', {}).get('name')
        return None