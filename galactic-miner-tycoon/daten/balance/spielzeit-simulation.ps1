param(
  [int]$NoHandTi = 0,
  [double]$TiRate = 0.3,
  [int]$NoRing = 0,
  [int]$HardHand = 0,
  [double]$Reserve = 1.0,
  [double]$HandMul = 1.0,
  [double]$DrillMul = 1.0,
  [string]$RocketStr = "1500,1200,800,400,150",
  [int]$BandsFar = 0,
  [double]$SpawnMul = 1.0,
  [int]$Quiet = 0
)
$Rocket = [double[]]($RocketStr -split ",")
$names = 'Eisen','Kupfer','Kohle','Kristall','Titan'
$stock = @(0.0,0.0,0.0,0.0,0.0)
$cap = @(100,100,100,100,100); $capLv = @(0,0,0,0,0)
$capVals = @(100,250,500,1000,2500); $capCost = @(0,50,100,200,400)
$binOn = @($true,$false,$false,$false,$false)
$drills = @(0,0,0,0,0); $banded = @(0,0,0,0,0); $dlvl = @(1,1,1,1,1)
$drillRate = @(1.0,0.8,0.6,0.4,$TiRate)
$drillCost = @( @(20,0,0,0,0), @(40,0,0,0,0), @(40,20,0,0,0), @(0,60,30,0,0), @(0,0,80,40,0) )
$lvlMult = @(1.0,1.5,2.0,2.5,3.0)
$feUp = @($null, @(25,0,0,0,0), @(50,10,0,0,0), @(100,30,0,0,0), @(200,60,20,0,0))
$upMul = @(0,1.25,2.5,5,10)
$spY = @(1,2,3,4,6); $spT = @(1.0,1.0,0.9,0.8,0.7)
$spCost = @($null, @(30,0,0,0,0), @(80,30,0,0,0), @(0,150,60,0,0), @(0,0,120,80,0)); $sp = 0
$rkCap = @(10,25,40,60,90,130)
$rkCost = @($null, @(30,0,0,0,0), @(60,0,0,0,0), @(100,20,0,0,0), @(0,60,20,0,0), @(0,150,60,20,0)); $rk = 0
$near = @(40,300,650,1150,1650); $avgD = @(120,450,850,1350,1800)
$init = @(3,2,2,1,1); $period = @(300,300,300,600,600); $maxV = @(10,8,6,5,4)
if ($NoRing -eq 1) { $near = @(900,850,800,750,700); $avgD = @(1300,1300,1300,1300,1300) }
$spawnStart = @(0.0, 1e9, 1e9, 1e9, 1e9)
$garage = $false; $rover = $false; $motorLv = 0; $cargoLv = 0
$handOre = 0.0; $drillOre = 0.0; $hb = @(0.0,0.0,0.0,0.0,0.0); $db = @(0.0,0.0,0.0,0.0,0.0)
$ms = @(
  @{n='Bohrer Eisen #1'; c=@(20,0,0,0,0); k='drill0'},
  @{n='Raum 2 Schmiede'; c=@(50,0,0,0,0); k='room2'},
  @{n='Rucksack 1'; c=@(30,0,0,0,0); k='rk'},
  @{n='Spitzhacke 2'; c=@(30,0,0,0,0); k='sp'},
  @{n='Kasten Kupfer'; c=@(40,0,0,0,0); k='bin1'},
  @{n='Raum 3 Maschinenhalle'; c=@(100,15,0,0,0); k='room3'},
  @{n='Rucksack 2'; c=@(60,0,0,0,0); k='rk'},
  @{n='Spitzhacke 3'; c=@(80,30,0,0,0); k='sp'},
  @{n='Kasten Kohle'; c=@(60,30,0,0,0); k='bin2'},
  @{n='Raum 4 Garage'; c=@(150,60,20,0,0); k='room4'},
  @{n='Rover'; c=@(150,80,30,0,0); k='rover'},
  @{n='Rucksack 3'; c=@(100,20,0,0,0); k='rk'},
  @{n='Kasten Kristall'; c=@(0,100,50,0,0); k='bin3'},
  @{n='Raum 5 Labor'; c=@(250,120,60,20,0); k='room5'},
  @{n='Kasten Titan'; c=@(0,0,150,60,0); k='bin4'},
  @{n='Spitzhacke 4'; c=@(0,150,60,0,0); k='sp'},
  @{n='Rucksack 4'; c=@(0,60,20,0,0); k='rk'},
  @{n='Spitzhacke 5'; c=@(0,0,120,80,0); k='sp'},
  @{n='Rucksack 5'; c=@(0,150,60,20,0); k='rk'},
  @{n='Raum 6 Hangar'; c=@(0,600,300,150,50); k='room6'},
  @{n='RAKETE'; c=$Rocket; k='rocket'}
)
$times = @{}
function Count($i,$t) {
  if ($t -lt $spawnStart[$i]) { return 0 }
  $c = $init[$i] + [math]::Floor(($t - $spawnStart[$i]) / ($period[$i] / $SpawnMul))
  return [math]::Min($maxV[$i], $c)
}
function Afford($cost, $avail) { for ($i=0;$i -lt 5;$i++) { if ($cost[$i] -gt $avail[$i] + 1e-9) { return $false } }; return $true }
function Pay($cost) { for ($i=0;$i -lt 5;$i++) { $script:stock[$i] -= $cost[$i] } }
$m = 0; $t = 0
while ($m -lt $ms.Count -and $t -lt 14400) {
  $t++
  $walk = 16.0; if ($rover) { $walk = 60.0 + 15*$motorLv }
  $carryCap = $rkCap[$rk] + 50*$cargoLv
  # drills income
  for ($i=0;$i -lt 5;$i++) {
    if ($drills[$i] -gt 0 -and $binOn[$i]) {
      $r = $drillRate[$i] * $lvlMult[$dlvl[$i]-1] * $DrillMul
      $inc = $r * $banded[$i] + [math]::Min($r, 50/180.0) * ($drills[$i]-$banded[$i])
      $room = $cap[$i] - $stock[$i]; if ($inc -gt $room) { $inc = [math]::Max(0.0,$room) }
      $stock[$i] += $inc; $drillOre += $inc; $db[$i] += $inc
    }
  }
  $cur = $ms[$m]; $mc = $cur.c
  # capacity needs
  $need = -1
  for ($i=0;$i -lt 5;$i++) { if ($mc[$i] -gt $cap[$i]) { $need = $i } }
  $target = $mc
  if ($need -ge 0) {
    $lv = $capLv[$need] + 1
    $cc = @(0,0,0,0,0); $cc[$need] = $capCost[$lv]; $target = $cc
  }
  # hand mining
  $best = -1; $bestDef = 0
  for ($i=0;$i -lt 5;$i++) {
    $def = $target[$i] - $stock[$i]
    if ($def -gt 0 -and $binOn[$i] -and -not ($NoHandTi -eq 1 -and $i -eq 4) -and ($sp -ge $i) -and (Count $i $t) -gt 0 -and $def -gt $bestDef) { $best = $i; $bestDef = $def }
  }
  if ($best -ge 0) {
    $rate = $spY[$sp] / $spT[$sp] * $HandMul; if ($HardHand -eq 1) { $rate = $rate * @(1.0,0.8,0.6,0.4,0.3)[$best] }
    $eff = $carryCap / ($carryCap/$rate + 2*$near[$best]/$walk + 4)
    $inc = [math]::Min($eff, [math]::Max(0.0,$cap[$best]-$stock[$best])); $stock[$best] += $inc; $handOre += $inc; $hb[$best] += $inc
  }
  # purchases
  $guard = 0
  while ($guard -lt 20) {
    $guard++
    $did = $false
    $mc = $cur.c
    if ($need -ge 0) {
      $lv = $capLv[$need] + 1
      $cc = @(0,0,0,0,0); $cc[$need] = $capCost[$lv]
      if (Afford $cc $stock) { Pay $cc; $capLv[$need]++; $cap[$need] = $capVals[$capLv[$need]]; $did = $true; $need = -1; for ($i=0;$i -lt 5;$i++) { if ($mc[$i] -gt $cap[$i]) { $need = $i } }; continue }
    } elseif (Afford $mc $stock) {
      Pay $mc
      switch ($cur.k) {
        'drill0' { $drills[0]++ }
        'room2' { $spawnStart[1] = $t }
        'rk' { $rk++ }
        'sp' { $sp++ }
        'bin1' { $binOn[1] = $true }
        'bin2' { $binOn[2] = $true }
        'bin3' { $binOn[3] = $true }
        'bin4' { $binOn[4] = $true }
        'room3' { $spawnStart[2] = $t; $room3 = $true }
        'room4' { $spawnStart[3] = $t; $garage = $true }
        'rover' { $rover = $true }
        'room5' { $spawnStart[4] = $t }
        'room6' { }
        'rocket' { }
      }
      $times[$cur.n] = $t
      $m++
      if ($m -ge $ms.Count) { break }
      $cur = $ms[$m]; $did = $true
      $need = -1; for ($i=0;$i -lt 5;$i++) { if ($cur.c[$i] -gt $cap[$i]) { $need = $i } }
      continue
    }
    # extras: spendable
    $mc = $cur.c
    $sa = @(0.0,0.0,0.0,0.0,0.0)
    for ($i=0;$i -lt 5;$i++) { if ($mc[$i] -gt 0) { $sa[$i] = [math]::Max(0.0, $stock[$i] - $Reserve*$mc[$i]) } else { $sa[$i] = $stock[$i] } }
    $handCan = $false; for ($i=0;$i -lt 5;$i++) { if (($mc[$i] - $stock[$i]) -gt 0 -and $binOn[$i] -and -not ($NoHandTi -eq 1 -and $i -eq 4) -and ($sp -ge $i) -and (Count $i $t) -gt 0) { $handCan = $true } }
    if (-not $handCan) { for ($i=0;$i -lt 5;$i++) { $sa[$i] = $stock[$i] } }
    if ($need -ge 0) { $sa[$need] = 0 }
    # bands (from room 3)
    if ($times.ContainsKey('Raum 3 Maschinenhalle')) {
      $lim = 2; if ($BandsFar -eq 1) { $lim = 4 }
      for ($i=0;$i -le $lim;$i++) {
        if ($drills[$i] -gt $banded[$i]) {
          $seg = [math]::Ceiling($avgD[$i]/4.0)
          $bc = @((2*$seg),0,0,0,0); if ($garage) { $bc[1] = $seg }
          if (Afford $bc $sa) { Pay $bc; $banded[$i]++; $did = $true; break }
        }
      }
      if ($did) { continue }
    }
    # drills
    for ($i=0;$i -lt 5;$i++) {
      if ($binOn[$i] -and $drills[$i] -lt (Count $i $t)) {
        $f = [math]::Pow(1.15, $drills[$i]); $dc = @(0,0,0,0,0)
        for ($j=0;$j -lt 5;$j++) { $dc[$j] = [math]::Round($drillCost[$i][$j]*$f) }
        if (Afford $dc $sa) { Pay $dc; $drills[$i]++; $did = $true; break }
      }
    }
    if ($did) { continue }
    # drill level ups
    for ($i=0;$i -lt 5;$i++) {
      if ($drills[$i] -gt 0 -and $dlvl[$i] -lt 5) {
        $L = $dlvl[$i]
        $uc = @(0,0,0,0,0)
        for ($j=0;$j -lt 5;$j++) {
          if ($i -eq 0) { $uc[$j] = $feUp[$L][$j] * $drills[$i] } else { $uc[$j] = $drillCost[$i][$j] * @(1.25,2.5,5,10)[$L-1] * $drills[$i] }
        }
        if (Afford $uc $sa) { Pay $uc; $dlvl[$i]++; $did = $true; break }
      }
    }
    if ($did) { continue }
    # rover upgrades
    if ($rover) {
      if ($motorLv -lt 4) { $mcst = @(0,100,40,0,0); if (Afford $mcst $sa) { Pay $mcst; $motorLv++; $did = $true; continue } }
      if ($cargoLv -lt 4) { $ccst = @(120,60,0,0,0); if (Afford $ccst $sa) { Pay $ccst; $cargoLv++; $did = $true; continue } }
    }
    break
  }
}
if ($Quiet -eq 0) {
  foreach ($k in $ms) { if ($times.ContainsKey($k.n)) { '{0,-24} {1,6:N1} min' -f $k.n, ($times[$k.n]/60.0) } else { '{0,-24} nicht erreicht' -f $k.n } }
  'Gesamt: {0:N1} min | Hand-Erz: {1:N0} | Bohrer-Erz: {2:N0} | Bohrer-Anteil: {3:P0}' -f ($t/60.0), $handOre, $drillOre, ($drillOre/[math]::Max(1.0,$handOre+$drillOre))
  $hs = ($hb | ForEach-Object { [math]::Round($_) }) -join ","; $ds = ($db | ForEach-Object { [math]::Round($_) }) -join ","; "Erz von Hand (Eisen,Kupfer,Kohle,Kristall,Titan): $hs"; "Erz von Bohrern: $ds"
  'Bohrer je Erz: ' + ($drills -join ',') + ' | BÃ¤nder: ' + ($banded -join ',') + ' | Bohrer-Level: ' + ($dlvl -join ',') + ' | Spitz ' + ($sp+1) + ' Ruck ' + $rk + ' Motor ' + $motorLv + ' Cargo ' + $cargoLv
} else {
  '{0:N1}' -f ($t/60.0)
}








