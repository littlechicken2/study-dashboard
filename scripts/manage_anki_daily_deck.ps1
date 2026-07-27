param(
    [ValidateSet("merge", "split")]
    [string]$Action = "merge"
)

$ErrorActionPreference = "Stop"

$AnkiUrl = "http://127.0.0.1:8766"
$TargetDeck = "French Daily Audio + Reading"
$Sources = @(
    @{
        Deck = "5000 Most Common French Words::[1] Main Course::[a] Option 1: Parisian French Audio::I) French to English (Start here)"
        Tag = "merge_source_pt1_parisian"
    },
    @{
        Deck = "5000 Most Common French Words Pt. 2::[1] Main Course::[b] Option 1: Canadian French Audio::I) French to English"
        Tag = "merge_source_pt2_canadian"
    },
    @{
        Deck = "5000 Most Common French Words::TCF Reading"
        Tag = "merge_source_tcf_reading"
    }
)

function Invoke-Anki {
    param(
        [string]$AnkiAction,
        [hashtable]$Params = @{}
    )

    $payload = @{
        action = $AnkiAction
        version = 6
        params = $Params
    } | ConvertTo-Json -Depth 12 -Compress

    $response = Invoke-RestMethod `
        -Uri $AnkiUrl `
        -Method Post `
        -ContentType "application/json" `
        -Body $payload

    if ($null -ne $response.error) {
        throw $response.error
    }
    return $response.result
}

function Find-Cards {
    param([string]$Query)
    return @(Invoke-Anki "findCards" @{ query = $Query })
}

function Find-Notes {
    param([string]$Query)
    return @(Invoke-Anki "findNotes" @{ query = $Query })
}

try {
    Invoke-Anki "version" | Out-Null
} catch {
    throw "Open Anki first, then run this script again."
}

Invoke-Anki "createDeck" @{ deck = $TargetDeck } | Out-Null

if ($Action -eq "merge") {
    foreach ($source in $Sources) {
        $query = 'deck:"' + $source.Deck + '"'
        $cards = Find-Cards $query
        $notes = Find-Notes $query

        if ($notes.Count -gt 0) {
            Invoke-Anki "addTags" @{
                notes = $notes
                tags = $source.Tag
            } | Out-Null
        }
        if ($cards.Count -gt 0) {
            Invoke-Anki "changeDeck" @{
                cards = $cards
                deck = $TargetDeck
            } | Out-Null
        }

        Write-Output ("Merged {0} cards from {1}" -f $cards.Count, $source.Deck)
    }
} else {
    foreach ($source in $Sources) {
        $query = 'deck:"' + $TargetDeck + '" tag:' + $source.Tag
        $cards = Find-Cards $query
        if ($source.Tag -eq "merge_source_tcf_reading") {
            $cards += Find-Cards ('deck:"' + $TargetDeck + '" tag:TCF_Reading')
            $cards = @($cards | Sort-Object -Unique)
        }

        if ($cards.Count -gt 0) {
            Invoke-Anki "createDeck" @{ deck = $source.Deck } | Out-Null
            Invoke-Anki "changeDeck" @{
                cards = $cards
                deck = $source.Deck
            } | Out-Null
        }

        Write-Output ("Restored {0} cards to {1}" -f $cards.Count, $source.Deck)
    }
}

$targetCards = Find-Cards ('deck:"' + $TargetDeck + '"')
Write-Output ("Target deck now contains {0} cards." -f $targetCards.Count)
