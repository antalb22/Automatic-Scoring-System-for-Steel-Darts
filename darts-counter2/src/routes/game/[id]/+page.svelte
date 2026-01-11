<script lang="ts">
    import ScoreDisplay from '$lib/components/ScoreDisplay.svelte';
    import ThrowBoxes from '$lib/components/ThrowBoxes.svelte';
    import ThrowControls from '$lib/components/ThrowControls.svelte';
    import EndTurnButton from '$lib/components/EndTurnButton.svelte';
    import Navbar from "$lib/components/Navbar.svelte";
    import {goto} from "$app/navigation";
    import {onDestroy, onMount} from 'svelte';
    import {calculateDartScore} from "$lib/utils/dartScore";
    import {getDistance, getTargetCoordinates} from "$lib/utils/targetUtils";
    import {browser} from '$app/environment';
    import DartboardHeatmap from "$lib/components/DartboardHeatmap.svelte";
    import {calculateSpread, findOptimalTarget} from "$lib/utils/dartMath";

    export let data: any;

    let game = data.game;
    let gameId = game.id;
    let mode = game.mode;
    let isTraining = mode === 'training';

    let trainingTargets = (data.targets || []).sort((a: any, b: any) => a.order - b.order);
    let currentTargetIndex = 0;
    let allSessionThrows = [...(data.throws || [])];
    let optimalTarget: any = null;
    let spreadStats: any = null;

    function getDistanceClass(distance: number): string {
        if (distance <= 2.0) return 'perfect';
        if (distance <= 6.0) return 'good';
        if (distance <= 12.0) return 'okay';
        return 'bad';
    }

    function formatScore(points: number, multiplier: number): any {
        if (points === undefined || points === null) return '';
        if (points === 50 || points === 25) return points;
        const base = Math.round(points / (multiplier || 1));

        if (multiplier === 3) return `T${base}`;
        if (multiplier === 2) return `D${base}`;

        return points;
    }

    function reconstructGameState(gameData: any, throwsData: any[]) {
        let players = [{id: 1, name: gameData.player1, score: parseInt(gameData.mode) || 0}];
        if (gameData.player2) players.push({id: 2, name: gameData.player2, score: parseInt(gameData.mode) || 0});

        let tIndex = 0;
        let pIndex = 0;
        let currentTurnThrows: any[] = [];
        let turnStartScore = players[0].score;
        let finished = false;
        let doubleOut = gameData.double_out;

        for (const t of throwsData) {
            if (isTraining) {
                if (currentTurnThrows.length === 3) {
                    tIndex++;
                    currentTurnThrows = [];
                }
                if (tIndex >= trainingTargets.length) {
                    finished = true;
                    break;
                }
                currentTurnThrows.push(t);
            } else {
                if (t.player_id !== players[pIndex].id) {
                    pIndex = (pIndex + 1) % players.length;
                    currentTurnThrows = [];
                    turnStartScore = players[pIndex].score;
                }
                const currentP = players[pIndex];
                const newScore = currentP.score - t.points;
                const isWinningThrow = newScore === 0 && (!doubleOut || t.multiplier === 2);

                if (newScore < 0 || newScore === 1 || (newScore === 0 && !isWinningThrow)) {
                    players[pIndex].score = turnStartScore;
                    currentTurnThrows = [];
                    pIndex = (pIndex + 1) % players.length;
                    turnStartScore = players[pIndex].score;
                    continue;
                }
                currentTurnThrows.push(t);
                players[pIndex].score = newScore;
                if (isWinningThrow) {
                    finished = true;
                    break;
                }
                if (currentTurnThrows.length === 3) {
                    pIndex = (pIndex + 1) % players.length;
                    currentTurnThrows = [];
                    turnStartScore = players[pIndex].score;
                }
            }
        }
        return {players, pIndex, currentTurnThrows, turnStartScore, finished, tIndex};
    }

    const restored = reconstructGameState(game, data.throws || []);
    let players = restored.players;
    let currentPlayerIndex = restored.pIndex;
    let currentThrows = restored.currentTurnThrows;
    let startingScore = restored.turnStartScore;
    let finished = restored.finished;

    if (isTraining) currentTargetIndex = restored.tIndex;

    let autoGame = game.auto === 1;
    let doubleOut = game.double_out;
    let interval: any;
    let previousThrowId: string | null = null;
    let autoProgress = false;

    $: currentPlayer = players[currentPlayerIndex];
    $: isTurnFull = currentThrows.length >= 3;
    $: controlsDisabled = isTurnFull || finished;
    $: endButtonLabel = finished ? (isTraining ? 'Finish Training' : 'End Game') : (isTraining ? 'Next Target' : 'End Turn');

    $: currentTarget = isTraining ? trainingTargets[currentTargetIndex] : null;
    $: targetLabel = currentTarget ? (currentTarget.type === 'S' ? '' : currentTarget.type) + (currentTarget.value === 25 ? 'BULL' : currentTarget.value) : '';
    $: targetCoords = currentTarget ? getTargetCoordinates(currentTarget.value, currentTarget.type) : {x: 0, y: 0};

    $: if (finished && isTraining && allSessionThrows.length >= 3) {
        spreadStats = calculateSpread(allSessionThrows);

        if (spreadStats.count > 0) {
            optimalTarget = findOptimalTarget(spreadStats.sigmaX, spreadStats.sigmaY);
            console.log("Optimal Strategy Calculated:", optimalTarget);
        }
    }

    async function processThrow(x: number, y: number, points: number, multiplier: number, throwId: string | null) {
        if (finished || isTurnFull) return;

        const rX = Math.round(x * 100) / 100;
        const rY = Math.round(y * 100) / 100;

        const currentScore = currentPlayer.score;
        let isCheckoutAttempt = false;

        if (!isTraining && doubleOut) {
            if (currentScore === 50) {
                isCheckoutAttempt = true;
            } else if (currentScore <= 40 && currentScore % 2 === 0) {
                isCheckoutAttempt = true;
            }
        }

        if (isTraining) {
            const rawDist = getDistance(rX, rY, targetCoords.x, targetCoords.y);
            const dist = Math.round(rawDist * 100) / 100;
            const targetX = Math.round(targetCoords.x * 100) / 100;
            const targetY = Math.round(targetCoords.y * 100) / 100;

            const area = (multiplier === 3 ? 'T' : multiplier === 2 ? 'D' : 'S') + points;
            const targetStr = currentTarget.type + currentTarget.value;

            let isHit = false;
            if (currentTarget.value === 50) isHit = points === 50;
            else if (currentTarget.value === 25) isHit = points === 25 || points === 50;
            else isHit = (area === targetStr);

            const throwData = {
                points, multiplier, x: rX, y: rY, distance: dist, isHit, area,
                targetX, targetY
            };

            currentThrows = [...currentThrows, throwData];
            allSessionThrows = [...allSessionThrows, throwData];

            const isLastTarget = currentTargetIndex === trainingTargets.length - 1;
            const isThirdDart = currentThrows.length === 3;
            const isTrainingFinished = isLastTarget && isThirdDart;

            if (isTrainingFinished) {
                finished = true;
            }

            await saveThrow(points, multiplier, throwId, isTrainingFinished, rX, rY, targetLabel, dist, targetX, targetY, false);

        } else {
            const newScore = currentPlayer.score - points;
            const isWinningThrow = newScore === 0 && (!doubleOut || multiplier === 2);

            if (newScore < 0 || newScore === 1 || (newScore === 0 && !isWinningThrow)) {
                alert('Bust!');
                players[currentPlayerIndex].score = startingScore;
                currentThrows = [];
                currentPlayerIndex = (currentPlayerIndex + 1) % players.length;
                startingScore = players[currentPlayerIndex].score;
                return;
            }

            currentThrows = [...currentThrows, {points, multiplier}];
            players[currentPlayerIndex].score = newScore;

            if (isWinningThrow) {
                finished = true;
            }

            await saveThrow(points, multiplier, throwId, isWinningThrow, rX, rY, null, null, null, null, isCheckoutAttempt);
        }

        if (!finished && currentThrows.length === 3) {
            scheduleAutoEndTurn();
        }
    }

    async function saveThrow(
        points: number, multiplier: number, throwId: string | null,
        isWinner: boolean, x: number | null, y: number | null,
        expectedTarget: string | null, distance: number | null = null,
        targetX: number | null = null, targetY: number | null = null,
        isCheckout: boolean = false // <--- ÚJ PARAMÉTER
    ) {
        if (!browser) return;
        try {
            await fetch('/api/throws', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    points, multiplier, throwId,
                    playerId: currentPlayer.id,
                    gameId: gameId,
                    isWinner,
                    playerName: currentPlayer.name,
                    x, y,
                    expected_target: expectedTarget,
                    distance, targetX, targetY,
                    isCheckout
                })
            });
        } catch (e) {
            console.error(e);
        }
    }

    function scheduleAutoEndTurn() {
        autoProgress = true;
        setTimeout(() => {
            if (!finished && currentThrows.length === 3) {
                endTurn();
            }
            autoProgress = false;
        }, 4000);
    }

    function endTurn() {
        autoProgress = false;
        if (currentThrows.length < 3) return;

        if (isTraining) {
            if (currentTargetIndex < trainingTargets.length - 1) {
                currentTargetIndex++;
                currentThrows = [];
            } else {
                finished = true;
            }
        } else {
            currentPlayerIndex = (currentPlayerIndex + 1) % players.length;
            startingScore = players[currentPlayerIndex].score;
            currentThrows = [];
        }
    }

    async function fetchThrows() {
        if (autoGame && browser && gameId && !finished) {
            try {
                const res = await fetch('/api/autothrows');
                if (!res.ok) return;
                const updated = await res.json();

                if (updated.success && updated.throw && updated.throw.throwId !== previousThrowId) {
                    const {x, y, throwId} = updated.throw;
                    previousThrowId = throwId;
                    const result = calculateDartScore(x, y);
                    await processThrow(x, y, result.score, result.multiplier, throwId);
                }
            } catch (e) {
            }
        }
    }

    async function handleUndo() {
        if (currentThrows.length > 0) {
            const last = currentThrows[currentThrows.length - 1];

            if (!isTraining) {
                players[currentPlayerIndex].score += last.points;
                players = players;
            }

            currentThrows = currentThrows.slice(0, -1);
            finished = false;
            autoProgress = false;

            if (browser) {
                await fetch('/api/throws', {
                    method: 'DELETE',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({gameId, playerId: currentPlayer.id})
                });
            }
        }
    }

    async function stopTracking() {
        if (browser) {
            try {
                await fetch('http://192.168.0.24:8000/game/stop/', {method: 'POST'}); //'http://localhost:8000/game/stop/'
                console.log("Kamerák leállítva.");
            } catch (e) {
                console.error("Stop error:", e);
            }
        }
    }

    onMount(() => {
        if (autoGame && browser) interval = setInterval(fetchThrows, 500);
    });
    onDestroy(() => {
        if (interval) clearInterval(interval);
        if (autoGame) stopTracking();
    });
</script>

<Navbar/>

<main>
    {#if data.game}
        {#if isTraining}
            <h2>{game.plan_name || "Training"}</h2>
            {#if !finished}
                {#if currentTarget}
                    <div class="target-display">
                        <span class="label">AIM FOR:</span>
                        <div class="target-circle {isTurnFull ? 'done' : ''}">
                            {targetLabel}
                        </div>
                    </div>
                {/if}
                <div class="throws-container">
                    {#each [0, 1, 2] as i}
                        {@const shot = currentThrows[i]}
                        <div class="throw-box-training {shot ? getDistanceClass(shot.distance) : 'empty'}">
                            {#if shot}
                                <div class="val">{formatScore(shot.points, shot.multiplier)}</div>
                                {#if shot.distance}
                                    <div class="dist">{shot.distance.toFixed(2)} cm</div>
                                {/if}
                            {:else}-
                            {/if}
                        </div>
                    {/each}
                </div>
            {:else if optimalTarget && spreadStats}
                <div class="stats-box">
                    <h4>Analysis & Tip</h4>

                    <p>Your Spread:
                        <strong>X: {spreadStats.sigmaX.toFixed(2)}cm, Y: {spreadStats.sigmaY.toFixed(2)}cm</strong>
                    </p>

                    <div class="recommendation">
                        <p>With your current accuracy, you achieve the highest score (expected average:
                            <strong>{(optimalTarget.ev * 3).toFixed(1)}</strong>) by aiming here:</p>

                        <div class="highlight-target">
                            {optimalTarget.name}
                        </div>

                        <small>X: {optimalTarget.x.toFixed(2)} cm, Y: {optimalTarget.y.toFixed(2)} cm</small>
                    </div>
                </div>
            {/if}
        {:else}
            <h2>{currentPlayer.name}'s Turn</h2>
            <ScoreDisplay score={currentPlayer.score}/>

            <ThrowBoxes throws={currentThrows.map(t => formatScore(t.points, t.multiplier))}/>
        {/if}

        {#if finished}
            <div class="winner-banner">
                <h3>{isTraining ? 'TRAINING COMPLETED!' : `WINNER: ${currentPlayer.name}`}</h3>
            </div>

            {#if isTraining && allSessionThrows.length > 0}
                <DartboardHeatmap
                        throws={allSessionThrows}
                        optimalTarget={optimalTarget ? {x: optimalTarget.x, y: optimalTarget.y} : null}
                        sigma={spreadStats ? {x: spreadStats.sigmaX, y: spreadStats.sigmaY} : null}
                />
            {/if}
        {/if}

        {#if !autoGame && !finished && !isTraining}
            <ThrowControls on:undo={handleUndo}
                           on:throw={(e) => processThrow(0, 0, e.detail.points, e.detail.multiplier, null)}/>
        {/if}

        <EndTurnButton
                onClick={finished ? () => goto('/') : endTurn}
                disabled={!finished && currentThrows.length < 3}
                label={endButtonLabel}
                progress={autoProgress}
        />
    {:else}
        <p>Loading...</p>
    {/if}
</main>

<style>
    main {
        text-align: center;
        padding: 20px;
        max-width: 500px;
        margin: 0 auto;
    }

    .target-circle {
        font-size: 4rem;
        font-weight: 800;
        color: #2563eb;
        border: 5px solid #2563eb;
        border-radius: 50%;
        width: 160px;
        height: 160px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
        background: white;
    }

    .target-circle.done {
        opacity: 0.5;
        transform: scale(0.9);
    }

    .throws-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 20px;
    }

    .throw-box-training {
        width: 70px;
        height: 70px;
        border: 2px solid #ddd;
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #f9f9f9;
        transition: background-color 0.3s;
    }

    .throw-box-training.perfect {
        background: #2e7d32;
        color: white;
        border-color: #1b5e20;
    }

    .throw-box-training.good {
        background: #66bb6a;
        color: white;
        border-color: #388e3c;
    }

    .throw-box-training.okay {
        background: #ffa726;
        color: white;
        border-color: #f57c00;
    }

    .throw-box-training.bad {
        background: #ef5350;
        color: white;
        border-color: #c62828;
    }

    .throw-box-training.empty {
        background: #f9f9f9;
        color: #333;
    }

    .val {
        font-size: 1.2rem;
        font-weight: bold;
    }

    .dist {
        font-size: 0.7rem;
    }

    .winner-banner {
        color: #2e7d32;
        font-size: 1.5em;
        font-weight: bold;
        margin: 20px 0;
        animation: pop 0.5s ease-out;
    }

    .undo-btn {
        margin: 20px auto;
        padding: 10px 20px;
        background: #f44336;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        display: block;
    }

    @keyframes pop {
        0% {
            transform: scale(0.8);
            opacity: 0;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
</style>