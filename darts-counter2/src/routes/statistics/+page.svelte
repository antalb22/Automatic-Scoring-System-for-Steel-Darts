<script lang="ts">
    import {onMount} from 'svelte';
    import Navbar from '$lib/components/Navbar.svelte';

    type Stat = {
        player: string;
        gamesFinished: number;
        wins: number;
        averageScore: number;
        averageAccuracy: number | null;
        first9Average: number;
        checkoutPercentage: number;
    };

    let stats: Stat[] = [];
    let searchQuery = '';
    let sortField: keyof Stat = 'averageScore';
    let sortDirection: 'asc' | 'desc' = 'desc';

    onMount(async () => {
        const res = await fetch('/api/statistics');
        stats = await res.json();
    });

    $: filteredStats = stats
        .filter(stat => stat.player.toLowerCase().includes(searchQuery.toLowerCase()))
        .sort((a, b) => {
            let valA = a[sortField];
            let valB = b[sortField];

            if (valA === null) valA = -1;
            if (valB === null) valB = -1;

            if (sortField === 'player') {
                return sortDirection === 'asc'
                    ? (valA as string).localeCompare(valB as string)
                    : (valB as string).localeCompare(valA as string);
            } else {
                return sortDirection === 'asc'
                    ? (valA as number) - (valB as number)
                    : (valB as number) - (valA as number);
            }
        });

    function setSort(field: keyof Stat) {
        if (sortField === field) {
            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            sortField = field;
            sortDirection = field === 'averageAccuracy' ? 'asc' : 'desc';
        }
    }

    function exportToCSV() {
        const headers = [
            "Player",
            "Matches Played",
            "Wins",
            "Avg Score (3-dart)",
            "First 9 Avg",
            "Checkout %",
            "Accuracy (cm)"
        ];

        const rows = filteredStats.map(stat => [
            `"${stat.player}"`,
            stat.gamesFinished,
            stat.wins,
            stat.averageScore.toFixed(2),
            stat.first9Average.toFixed(2),
            stat.checkoutPercentage.toFixed(2),
            stat.averageAccuracy !== null ? stat.averageAccuracy.toFixed(2) : ""
        ]);

        const csvContent = [
            headers.join(","),
            ...rows.map(row => row.join(","))
        ].join("\n");

        const blob = new Blob([csvContent], {type: 'text/csv;charset=utf-8;'});
        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `darts_statistics_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
</script>

<Navbar/>

<main>
    <div class="header-row">
        <h1>Player Statistics</h1>
        <button class="export-btn" on:click={exportToCSV}>
            Export to CSV
        </button>
    </div>

    <input
            bind:value={searchQuery}
            class="search-input"
            placeholder="Search player..."
            type="text"
    />

    <div class="table-container">
        <table>
            <thead>
            <tr>
                <th on:click={() => setSort('player')}>
                    Player {sortField === 'player' ? (sortDirection === 'asc' ? '▲' : '▼') : ''}</th>
                <th on:click={() => setSort('gamesFinished')}>
                    Matches {sortField === 'gamesFinished' ? (sortDirection === 'asc' ? '▲' : '▼') : ''}</th>
                <th on:click={() => setSort('wins')}>
                    Wins {sortField === 'wins' ? (sortDirection === 'asc' ? '▲' : '▼') : ''}</th>
                <th on:click={() => setSort('averageScore')}>
                    Avg Score {sortField === 'averageScore' ? (sortDirection === 'asc' ? '▲' : '▼') : ''}</th>
                <th on:click={() => setSort('first9Average')}>
                    First 9 Avg {sortField === 'first9Average' ? (sortDirection === 'asc' ? '▲' : '▼') : ''}</th>
                <th on:click={() => setSort('checkoutPercentage')}>
                    Checkout % {sortField === 'checkoutPercentage' ? (sortDirection === 'asc' ? '▲' : '▼') : ''}</th>
                <th on:click={() => setSort('averageAccuracy')}>
                    Accuracy (Error) {sortField === 'averageAccuracy' ? (sortDirection === 'asc' ? '▲' : '▼') : ''}</th>
            </tr>
            </thead>
            <tbody>
            {#each filteredStats as stat}
                <tr>
                    <td class="player-name">{stat.player}</td>
                    <td>{stat.gamesFinished}</td>
                    <td>{stat.wins}</td>
                    <td class="score">{stat.averageScore.toFixed(2)}</td>
                    <td class="score">{stat.first9Average.toFixed(2)}</td>
                    <td>
                        {#if stat.checkoutPercentage > 0}
                            {stat.checkoutPercentage.toFixed(1)}%
                        {:else}
                            -
                        {/if}
                    </td>
                    <td class="accuracy">
                        {#if stat.averageAccuracy !== null}
                            {stat.averageAccuracy.toFixed(2)} cm
                        {:else}
                            -
                        {/if}
                    </td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>
</main>

<style>
    main {
        max-width: 1000px;
        margin: 2rem auto;
        padding: 0 20px;
    }

    h1 {
        text-align: center;
        margin-bottom: 30px;
    }

    input.search-input {
        margin-bottom: 1.5rem;
        width: 100%;
        max-width: 400px;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #ccc;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }

    .table-container {
        overflow-x: auto;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        background: white;
    }

    th, td {
        padding: 1rem;
        text-align: center;
        border-bottom: 1px solid #eee;
    }

    th {
        cursor: pointer;
        background-color: #333;
        color: white;
        user-select: none;
        white-space: nowrap;
    }

    th:hover {
        background-color: #555;
    }

    tr:nth-child(even) {
        background-color: #f8f9fa;
    }

    tr:hover {
        background-color: #f1f1f1;
    }

    .player-name {
        font-weight: bold;
        text-align: left;
    }

    .score {
        font-weight: bold;
        color: #2e7d32;
    }

    .accuracy {
        font-weight: bold;
        color: #d84315;
    }

    .header-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin-bottom: 30px;
        position: relative;
    }

    h1 {
        margin: 0;
    }

    .export-btn {
        background-color: #2e7d32;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
        font-size: 0.9rem;
        transition: background-color 0.2s;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .export-btn:hover {
        background-color: #1b5e20;
    }
</style>