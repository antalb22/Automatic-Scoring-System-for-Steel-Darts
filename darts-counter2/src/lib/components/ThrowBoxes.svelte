<script lang="ts">
    export let throws: number[];
</script>

<div class="throw-boxes">
    {#each [0, 1, 2] as i}
        <div class="box">{throws[i] ?? ''}</div>
    {/each}
</div>

<style>
    .throw-boxes {
        margin: 1rem auto;
        display: flex;
        gap: 1rem;
        justify-content: center;
    }

    .box {
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #888;
        border-radius: 10px;
        font-size: 1.3rem;
        font-weight: bold;
        background-color: #f9f9f9;
    }
</style>
