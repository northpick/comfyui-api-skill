"""Batch Bernini animation generator"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from gen import submit

def go(name, prompt, ref_img="subai_normal_v10.png", prefix=None, view="pure"):
    p = prefix or f"anim_{name}"
    return submit("bernini", [
        {"nodeId": "182", "fieldName": "image", "fieldValue": ref_img},
        {"nodeId": "152", "fieldName": "value", "fieldValue": prompt},
        {"nodeId": "155", "fieldName": "filename_prefix", "fieldValue": p},
        {"nodeId": "134", "fieldName": "width", "fieldValue": 960},
        {"nodeId": "134", "fieldName": "height", "fieldValue": 1280},
        {"nodeId": "134", "fieldName": "length", "fieldValue": 25},
    ], output_name=p, timeout_min=20)


if __name__ == "__main__":
    name = sys.argv[1]
    print(f"=== {name} ===")

    JOBS = {
        # NPCs
        "chef_stir": {
            "ref": "ref_chef_n.png",
            "prompt": "Giant chef puppet 3/4 SIDE view FACING LEFT, full body. 2.5 meters tall, obese silhouette stuffed with canvas. Wears flour-sack chef hat stamped with faded ration text. Face is ceramic mask with painted-on smile -- lower right corner chipped off revealing hollow black interior. Apron stained with dark grease and rusty stains. Three kitchen knives and a wooden spoon in apron pocket. Giant brass butterfly-shaped key protrudes from spine at shoulder-blade level, slowly rotating. Right hand holds huge chef knife. Left hand holds cracked white porcelain plate. Standing at invisible stove. Right arm moves in repetitive stirring motion -- pushing knife forward in arc, pulling back. Brass key on back rotates one full turn per stir cycle. Ceramic smile never changes. Steam rises from below. Mechanical trapped-in-loop movements. Pure white bg, empty void. Full body in frame. 2D flat cartoon cel-shaded, thick outlines. 25f 16fps loop."
        },
        "chef_ce_stir": {
            "ref": "ref_chef_ce.png",
            "prompt": "Giant gingerbread chef 3/4 SIDE view FACING LEFT, full body. 2.5 meters tall. Wears white chef hat. Face is a cookie mask with painted smile, cute chip at edge. Apron covered in colorful frosting and caramel stains with three hand-drawn smiley faces. Back has giant lollipop key instead of brass key, slowly rotating. Right hand holds huge knife. Left hand holds cracked porcelain plate. Standing at invisible stove. Right arm stirs mechanically -- repeating loop. Candy-colored. Warm cozy slightly eerie atmosphere. Pure white bg, empty void. Full body in frame. 2D flat cartoon cel-shaded, thick outlines. 25f 16fps loop."
        },
        "rabbi_polish": {
            "ref": "ref_rabbi_n.png",
            "prompt": "Pewter rabbit soldier 3/4 SIDE view FACING LEFT, full body. 1.4 meters tall. Cast from matte lead-gray metal with tiny bubble pitting. Right ear straight up, left ear has bullet hole causing it to flop. Whiskers are six guitar strings (one missing). Eyes are mismatched buttons. Wears only right half of blue-gray military vest -- left side exposes lead chest engraved with words. Holds broken rifle missing all internal mechanisms, 43 tally marks carved into stock. Right hand grips worn-down shoe brush. Sitting on invisible crate. Frantically polishes broken rifle with brush -- obsessive back-and-forth. Wrist moves rapidly. Occasionally pauses, stares at nothing, resumes polishing even more intensely. Left ear flops with each movement. Trapped in compulsive cleaning loop. Pure white bg, empty void. Full body in frame. 2D flat cartoon cel-shaded, thick outlines. 25f 16fps loop."
        },
        "nord_sleep": {
            "ref": "ref_nord_n.png",
            "prompt": "Battered teddy bear 3/4 SIDE view FACING LEFT, full body. About 50cm tall. Light brown fur has 60 percent bald patches revealing rough linen underneath. Dark stain on belly. Right ear half gone with straw stuffing poking out. Left button eye missing (loose thread), right eye cracked yellow glass bead. Crossed leather ammo belts on chest holding two rusted M24 stick grenades, each pull-ring has small bell tied to it. Sitting slumped against invisible wall. Head nods forward falling asleep -- then jerks up suddenly catching himself awake. Slow descent, snap awake, repeat. Belly rises and falls with deep breaths. Bells jingle faintly with each jerk. Remaining button eye flickers. Deeply tired, always about to fall asleep. Pure white bg, empty void. Full body in frame. 2D flat cartoon cel-shaded, thick outlines. 25f 16fps loop."
        },
        "jester_float": {
            "ref": "ref_jester_n.png",
            "prompt": "Transparent clown figure 3/4 SIDE view FACING LEFT, full body. 90 percent transparent elongated human shape. Wears faded colorful one-piece clown suit. Tattered translucent ball follows at feet. Only visible parts are bright red lips and pale yellow teeth frozen in permanent exaggerated smile. Eyes are pure emptiness. Floating weightlessly, drifting slowly up and down like leaf on water. Body sways gently. Permanent smile sometimes wavers -- crack appears in red lip for fraction of a second before repairing. Transparent suit ripples as if underwater. Tilts head slightly as if observing. Eerily silent unsettling. Pure white bg, empty void. Full body in frame. 2D flat cartoon cel-shaded, thick outlines. 25f 16fps loop."
        },
        "boss_idle": {
            "ref": "ref_boss_n.png",
            "prompt": "5-meter-tall figure 3/4 SIDE view FACING LEFT, full body. Lower body is massive bell-shaped crinoline skirt brutally assembled from tank armor plates and barbed wire. Upper body wears dark red imperial marshal uniform fused with skin, covered in melted medals. Head has crown of seven broken bayonets pointing outward. Face is smooth white porcelain mask with red pulsing light from within. Standing motionless with absolute stillness. Then slowly raises arms out to sides like conductor preparing to begin. Armor plates scrape together. Red light behind mask pulses rhythmically like heartbeat. Bayonets catch light. Imposing terrifying majestic monument of war. Pure white bg, empty void. Full body in frame. 2D flat cartoon cel-shaded, thick outlines. 25f 16fps loop."
        },
        "boss_ce_idle": {
            "ref": "ref_boss_ce.png",
            "prompt": "Towering motherly figure 3/4 SIDE view FACING LEFT, full body. Tank-crinoline skirt covered in layers of beautiful wedding-cake frosting, sugar flowers, cream decorations -- metal base flickers through occasionally. Marshal uniform pristine and new, medals transformed into shiny colorful candies. Bayonet crown now ring of colorful lollipops. Porcelain mask glows with warm golden light, eternal smile warm and loving. Stands with arms slightly open as if welcoming child for hug. Warm golden light radiates. Tilts head slightly with maternal warmth. Then GLITCH -- for 0.2 seconds mask flickers cold red, frosting flashes to tank armor, candy crown becomes bayonets -- snaps back to sweet motherly form. Flicker repeats every few seconds. Something wrong beneath the sweetness. Pure white bg, empty void. Full body in frame. 2D flat cartoon cel-shaded, thick outlines. 25f 16fps loop."
        },
    }

    job = JOBS.get(name)
    if not job:
        print(f"Unknown job: {name}. Available: {list(JOBS.keys())}")
        sys.exit(1)

    r = go(name, job["prompt"], ref_img=job["ref"])
    print(f"DONE {name}: {r}")
