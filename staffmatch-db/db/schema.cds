namespace staffmatch;

// ─────────────────────────────────────────
// TABELLE DI RIFERIMENTO
// ─────────────────────────────────────────

entity Skill {
  key ID          : UUID;
  codice          : String(20);   // es. SAP_FI, S4HANA
  descrizione     : String(200);
  livelloMin      : Integer;      // 1
  livelloMax      : Integer;      // 5
}

entity Mansione {
  key ID          : UUID;
  codice          : String(50);   // es. SENIOR_CONSULTANT
  descrizione     : String(200);
  lcr             : Decimal(10,2); // tariffa giornaliera di riferimento
}

// ─────────────────────────────────────────
// ENTITÀ OPERATIVE — aggiornamento settimanale
// ─────────────────────────────────────────

entity Risorsa {
  key ID                : UUID;
  nome                  : String(100);
  cognome               : String(100);
  email                 : String(200);
  mansione              : Association to Mansione;
  livello               : String(50);   // Junior / Senior / Manager / ...
  costoOrario           : Decimal(10,2);
  disponibilita         : Integer;      // % disponibilità attuale
  termineProgetto       : Date;         // quando si libera — chiave per il matching
  offshore              : Boolean;
  stagista              : Boolean;
  movimentoInCorso      : Boolean;      // ingresso/uscita dalla practice — solo stato
  lingua                : String(200);  // es. Italiano, Inglese
}

entity RisorsaSkill {
  key risorsa     : Association to Risorsa;
  key skill       : Association to Skill;
  livello         : Integer;            // livello dichiarato 1-5
}

entity Need {
  key ID          : UUID;
  cliente         : String(200);
  iniziativa      : String(200);
  descrizione     : String(2000);
  osr             : String(200);        // Opportunity Sales Representative
  dataAvvio       : Date;
  priorita        : Integer;            // calcolata dal motore AI
  status          : String(50);         // New / Active / Closed
  ipotesi         : String(1000);
}

entity NeedSkill {
  key need        : Association to Need;
  key skill       : Association to Skill;
  livelloMinimo   : Integer;            // livello minimo accettabile
  mansione        : Association to Mansione;
  percentuale     : Integer;            // allocazione % richiesta
}

// ─────────────────────────────────────────
// ALLOCAZIONE — collega Risorsa a Need/Progetto
// ─────────────────────────────────────────

entity Allocazione {
  key ID          : UUID;
  risorsa         : Association to Risorsa;
  need            : Association to Need;
  percentuale     : Integer;
  dataInizio      : Date;
  dataFine        : Date;
  ruolo           : String(100);        // ruolo nel progetto
  settore         : String(100);        // settore cliente — peso nel matching AI
}

// ─────────────────────────────────────────
// OUTPUT AI — storico matching
// ─────────────────────────────────────────

entity MatchResult {
  key ID          : UUID;
  need            : Association to Need;
  risorsa         : Association to Risorsa;
  score           : Integer;            // 0-100
  motivazione     : String(2000);
  confermato      : Boolean;
  dataMatching    : DateTime;
}