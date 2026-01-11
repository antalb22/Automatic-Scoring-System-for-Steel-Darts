<script lang="ts">
    import {goto} from '$app/navigation';
</script>

<nav>
    <button on:click={() => goto('/training')}>Training</button>
    <button on:click={() => goto('/')}>New Game</button>
    <button on:click={() => goto('/history')}>History</button>
    <button on:click={() => goto('/statistics')}>Statistics</button>
</nav>

<style>
    nav {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        background-color: #f0f0f0;
        justify-content: center;
    }

    button {
        background: none;
        border: none;
        font-size: 1rem;
        cursor: pointer;
        padding: 0.5rem 1rem;
    }

    button:hover {
        background-color: #ddd;
        border-radius: 6px;
    }
</style>
