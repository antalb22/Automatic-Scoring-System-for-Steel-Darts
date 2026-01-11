<script lang="ts">
    export let disabled: boolean;
    export let onClick: () => void;
</script>

<button on:click={onClick} disabled={disabled}>
    Start Game
</button>

<style>
    button {
        margin-top: 1rem;
        width: 100%;
        padding: 0.6rem;
        background-color: #28a745;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 1rem;
    }

    button:disabled {
        background-color: #aaa;
    }
</style>
