# Time Warp II: Conquest — self-hosted asset downloader
# Tenor GIFs are embedded fair-use commentary — DO NOT download them, use the URLs in manifest.json directly in <img>/<iframe>.
# This script pulls only the Wikimedia / royalty-free assets that we self-host.
#
# Run from a PowerShell prompt with outbound network access:
#   cd "F:\Michael's\ACE\US History\Time-Warp-II-Conquest"
#   powershell -ExecutionPolicy Bypass -File memes\download_assets.ps1

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

# Use Wikimedia's Special:FilePath redirect for canonical "always-current" URLs.
# This avoids hash-folder URL brittleness.
$wm = "https://commons.wikimedia.org/wiki/Special:FilePath/"

$jobs = @(
    # Hub showpiece (Aivazovsky 1887)
    @{ url = "${wm}Ivan_Aivazovsky_-_Ship_in_the_Stormy_Sea.jpg"; out = "memes\hub\storm_galleon.jpg" },
    # Hub backup (Eertvelt + Bakhuizen)
    @{ url = "${wm}Andries_van_Eertvelt_-_Ships_in_Stormy_Seas.jpg"; out = "memes\hub\storm_galleon_eertvelt.jpg" },
    @{ url = "${wm}Bakhuizen_-_Storm_op_de_Hollandse_kust,_1682_with_frame.jpg"; out = "memes\hub\storm_galleon_bakhuizen.jpg" },
    # Hub UI accents
    @{ url = "${wm}Old_Roger.png"; out = "memes\hub\jolly_roger.png" },
    @{ url = "${wm}Parchment.00.jpg"; out = "memes\hub\parchment.jpg" },

    # Columbus mutiny background
    @{ url = "${wm}Engagement_between_a_Spanish_galleon_and_a_Dutch_ship.jpg"; out = "memes\columbus_mutiny\galleon_battle.jpg" },
    @{ url = "${wm}Spanish_Galleon_Firing_its_Cannon.jpg"; out = "memes\columbus_mutiny\galleon_cannon.jpg" },

    # Corte-Real fog
    @{ url = "${wm}Theodor_Kittelsen_-_The_Ship_Albatros_in_Storm_-_NG.K%26H.B.00450_-_National_Museum_of_Art,_Architecture_and_Design.jpg"; out = "memes\cortereal_fog\albatros_in_storm.jpg" },

    # Da Gama
    @{ url = "${wm}Vasco_da_Gama_op_audi%C3%ABntie_bij_koning_van_Calcutta,_RP-P-1878-A-1875.jpg"; out = "memes\dagama_resistance\calicut_audience.jpg" },
    @{ url = "${wm}Engagement_between_a_Spanish_galleon_and_a_Dutch_ship.jpg"; out = "memes\dagama_resistance\naval_battle.jpg" },

    # Magellan / Mactan
    @{ url = "${wm}Magellans_Ermordung.jpg"; out = "memes\magellan_mactan\mactan_woodcut.jpg" },
    @{ url = "${wm}Magellans_death.jpg"; out = "memes\magellan_mactan\magellan_death_painting.jpg" },
    @{ url = "${wm}Magellan_expedition_by_Stradanus.jpg"; out = "memes\magellan_mactan\stradanus_allegory.jpg" },

    # Narvaez (hurricane + map)
    @{ url = "${wm}A_Clipper_ship_in_a_hurricane_LCCN90716150.jpg"; out = "memes\narvaez_swamp\clipper_hurricane.jpg" },
    @{ url = "${wm}Expedition_Cabeza_de_Vaca_Karte.png"; out = "memes\narvaez_swamp\cabeza_de_vaca_route.png" },

    # Raleigh
    @{ url = "${wm}Sir_Walter_Raleigh_in_the_Tower_by_Henry_Wallis.jpg"; out = "memes\raleigh_executioner\raleigh_in_tower.jpg" },
    @{ url = "${wm}Execution_of_Sir_Walter_Raleigh.jpg"; out = "memes\raleigh_executioner\execution_engraving.jpg" },
    @{ url = "${wm}Beul_met_zwaard,_RP-P-OB-19.904.jpg"; out = "memes\raleigh_executioner\executioner_etching.jpg" }
)

$ok = 0; $fail = 0
foreach ($j in $jobs) {
    $dir = Split-Path $j.out -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Write-Host ">>> $($j.out)"
    try {
        Invoke-WebRequest -Uri $j.url -OutFile $j.out -UseBasicParsing -MaximumRedirection 10
        $sz = (Get-Item $j.out).Length
        if ($sz -lt 5000) {
            Write-Host "    WARN: file is $sz bytes (likely an HTML error page)" -ForegroundColor Yellow
            $fail++
        } else {
            Write-Host "    OK ($([math]::Round($sz/1024)) KB)" -ForegroundColor Green
            $ok++
        }
    } catch {
        Write-Host "    FAIL: $_" -ForegroundColor Red
        $fail++
    }
}

Write-Host ""
Write-Host "Done. $ok ok, $fail failed." -ForegroundColor Cyan
Write-Host "Tenor GIFs are NOT downloaded - use the embed URLs from memes\manifest.json directly in your HTML." -ForegroundColor Cyan
