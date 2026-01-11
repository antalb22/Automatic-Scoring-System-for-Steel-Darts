<script lang="ts">
    import {goto} from '$app/navigation';
    import Navbar from "$lib/components/Navbar.svelte";
    import StartButton from '$lib/components/StartButton.svelte';
    import {onMount} from "svelte";
    import {browser} from "$app/environment";

    type TrainingPlan = {
        id: number;
        name: string;
    };

    let cameraInitialized = false;
    let gameMode: 301 | 501 | "training" = 501;
    let doubleOut = true;
    let playerCount: 1 | 2 = 1;
    let player1 = '';
    let player2 = '';
    let autoGame = false;
    let ip = '192.168.0.24'; //localhost
    let trainingPlans: TrainingPlan[] = [];
    let selectedTrainingPlan: number | null = null;

    async function startGame() {
        const res = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                player1,
                player2: (gameMode !== 'training' && playerCount === 2) ? player2 : null,
                mode: gameMode,
                doubleOut,
                autoGame: gameMode === 'training' ? true : autoGame,
                trainingPlanId: gameMode === 'training' ? selectedTrainingPlan : null
            })
        });

        const data = await res.json();

        if (autoGame || gameMode === 'training') {
            try {
                await fetch(`http://${ip}:8000/game/init/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        gameId: data.id,
                        player2: (gameMode !== 'training' && playerCount === 2) ? player2 : null,
                    })
                });
            } catch (e) {
                console.error("Hiba a Python backend inicializálásakor:", e);
            }
        }

        if (data.success) {
            await goto(`/game/${data.id}`);
        } else {
            alert("Failed to start game: " + data.error);
        }
    }

    onMount(async () => {
        if (!browser) return;

        const resTraining = await fetch('/api/training');
        if (resTraining.ok) {
            trainingPlans = await resTraining.json();
            if (trainingPlans.length > 0) {
                selectedTrainingPlan = trainingPlans[0].id;
            }
        }

        if (!cameraInitialized) {
            try {
                const resTurnOn = await fetch(`http://${ip}:8000/game/turnon/`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                });
                if (resTurnOn.ok) {
                    console.log('Kamerák elindítva');
                    cameraInitialized = true;
                }
            } catch (e) {
                console.log("Nem sikerült elérni a kamerákat", e);
            }
        }
    });
</script>

<Navbar/>

<main>
    <h1>Darts Game Setup</h1>

    <div class="form-group">
        <label for="gamemode">Game Mode:</label>
        <select bind:value={gameMode} id="gamemode">
            <option value={301}>301</option>
            <option value={501}>501</option>
            <option value="training">Training Plan</option>
        </select>
    </div>

    {#if gameMode === "training"}
        <div class="form-group">
            <label for="training-plan">Training Plan:</label>
            <select id="training-plan" bind:value={selectedTrainingPlan}>
                {#each trainingPlans as plan}
                    <option value={plan.id}>
                        {plan.name}
                    </option>
                {/each}
            </select>
        </div>

        <div class="form-group">
            <label for="training-player">Player Name:</label>
            <input id="training-player" bind:value={player1} type="text"/>
        </div>
    {:else }
        <div class="form-group">
            <label for="doubleout">Double Out:</label>
            <input bind:checked={doubleOut} id="doubleout" type="checkbox"/>
        </div>

        <div class="form-group">
            <label for="players">Players:</label>
            <select bind:value={playerCount} id="players">
                <option value={1}>1 Player</option>
                <option value={2}>2 Players</option>
            </select>
        </div>

        <div class="form-group">
            <label for="player1">Player 1 Name:</label>
            <input bind:value={player1} id="player1" type="text"/>
        </div>

        {#if playerCount === 2}
            <div class="form-group">
                <label for="player2">Player 2 Name:</label>
                <input id="player2" type="text" bind:value={player2}/>
            </div>
        {/if}

        <div class="form-group">
            <label for="autogame">Auto Game:</label>
            <input bind:checked={autoGame} id="autogame" type="checkbox"/>
        </div>
    {/if}

    <StartButton disabled={
        !player1 ||
        (gameMode !== 'training' && playerCount === 2 && !player2) ||
        (gameMode === 'training' && !selectedTrainingPlan) ||
        (!cameraInitialized && (autoGame || gameMode === 'training')) ||
        (autoGame && playerCount === 2) //ToDo
    }
                 onClick={startGame}
    />
</main>

<style>
    main {
        max-width: 400px;
        margin: 2rem auto;
        text-align: center;
    }

    .form-group {
        margin-bottom: 1rem;
        text-align: left;
    }

    label {
        display: block;
        margin-bottom: 0.3rem;
    }

    input,
    select {
        width: 100%;
        padding: 0.4rem;
        border-radius: 6px;
        border: 1px solid #ccc;
    }
</style>