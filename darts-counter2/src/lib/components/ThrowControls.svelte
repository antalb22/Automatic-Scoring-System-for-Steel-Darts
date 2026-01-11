<script lang="ts">
    import {createEventDispatcher} from 'svelte';

    const dispatch = createEventDispatcher();

    let multiplier = 1;
    export let disabled = false;

    function toggleMultiplier(value: number) {
        multiplier = multiplier === value ? 1 : value;
    }

    function throwPoints(base: number) {
        if (base === 25 && multiplier === 3) return;

        dispatch('throw', {points: base * multiplier, multiplier});

        multiplier = 1;
    }

    function undo() {
        dispatch('undo');
    }
</script>

<div class="container">
    <div class="grid">
        {#each Array.from({length: 20}, (_, i) => i + 1) as n}
            <button on:click={() => throwPoints(n)} disabled={disabled}>{n}</button>
        {/each}

        <button disabled={multiplier === 3 || disabled} on:click={() => throwPoints(25)}>25</button>
        <button disabled={disabled} on:click={() => throwPoints(0)}>0</button>
        <button class:active={multiplier === 2} disabled={disabled} on:click={() => toggleMultiplier(2)}>Double</button>
        <button class:active={multiplier === 3} disabled={disabled} on:click={() => toggleMultiplier(3)}>Triple</button>
        <button on:click={undo}>Undo</button>
    </div>
</div>

<style>
    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(5, 70px);
        gap: 0.75rem;
        justify-content: center;
    }

    button {
        width: 70px;
        height: 70px;
        font-size: 1.2rem;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        background-color: #eee;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    button:hover {
        background-color: #ddd;
    }

    button.active {
        background-color: #0070f3;
        color: white;
    }

    button:disabled {
        background-color: #ccc;
        color: #666;
        cursor: not-allowed;
    }
</style>


