<script lang="ts">
    export let disabled: boolean;
    export let onClick: () => void;
    export let label: string = "End Turn";
    export let progress: boolean = false;
</script>

<div class="end-turn-wrapper">
    <button
            class="end-turn-button"
            disabled={disabled}
            on:click={onClick}
    >
        <span class="label-text">{label}</span>
        {#if progress}
            <span class="loading-bar"></span>
        {/if}
    </button>
</div>

<style>
    .end-turn-wrapper {
        margin-top: 1.5rem;
        display: flex;
        justify-content: center;
    }

    .end-turn-button {
        position: relative;
        width: 200px;
        height: 50px;
        font-size: 1.1rem;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        color: white;
        background-color: #ccc;
        overflow: hidden;
    }

    .end-turn-button:enabled {
        background-color: #28a745;
        cursor: pointer;
    }

    .end-turn-button:disabled {
        cursor: not-allowed;
    }

    .loading-bar {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 4px;
        background-color: #007bff;
        width: 100%;
        transform: scaleX(0);
        transform-origin: left;
        animation: fillBar 4s linear forwards;
    }

    @keyframes fillBar {
        from {
            transform: scaleX(0);
        }
        to {
            transform: scaleX(1);
        }
    }
</style>
