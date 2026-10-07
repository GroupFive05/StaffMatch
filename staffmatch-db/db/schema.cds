namespace staffmatch;

entity Skill {
  key id          : String(20);
  nome            : String(100);
  categoria       : String(100);
  descrizione     : String(500);
}

entity Ruolo {
  key id          : String(20);
  nome            : String(100);
  seniority       : String(50);
  descrizione     : String(500);
  costoOrario     : Decimal(10,2);
}

entity GruppoRuolo {
  key id          : String(20);
  nome            : String(100);
  descrizione     : String(500);
  ruoliIds        : String(500);
}

entity Risorsa {
  key id              : String(20);
  nome                : String(100);
  cognome             : String(100);
  email               : String(200);
  dataNascita         : Date;
  ruoloId             : String(20);
  costoOrario         : Decimal(10,2);
  lingue              : String(200);
  isActive            : Boolean default true;
  passwordHash        : String(200);
  gruppoRuoloIds      : String(200);
  disponibilita       : Integer;
  termineProgetto     : Date;
  offshore            : Boolean default false;
  stagista            : Boolean default false;
  movimentoInCorso    : Boolean default false;
}

entity RisorsaSkill {
  key risorsaId   : String(20);
  key skillId     : String(20);
  livello         : Integer;
}

entity Opportunity {
  key id                  : String(30);
  titolo                  : String(200);
  cliente                 : String(200);
  referenteNome           : String(100);
  referenteCognome        : String(100);
  managerId               : String(20);
  dataInizio              : Date;
  dataFinePrevista        : Date;
  stato                   : String(50);
  descrizione             : String(2000);
  priorita                : Integer default 0;
}

entity OpportunitySkill {
  key opportunityId   : String(30);
  key skillId         : String(20);
  livelloMinimo       : Integer;
}

entity OpportunitySlot {
  key opportunityId       : String(30);
  key slotIndex           : Integer;
  mansioneId              : String(20);
  percentualeAllocazione  : Integer;
}

entity Progetto {
  key id                  : String(30);
  nome                    : String(200);
  cliente                 : String(200);
  referenteNome           : String(100);
  referenteCognome        : String(100);
  managerId               : String(20);
  skillPrincipaleId       : String(20);
  skillSecondarie         : String(500);
  dataInizio              : Date;
  dataFinePrevista        : Date;
  stato                   : String(50);
  descrizione             : String(2000);
}

entity Allocazione {
  key id              : String(30);
  risorsaId           : String(20);
  progettoId          : String(30);
  percentuale         : Integer;
  dataInizio          : Date;
  dataFine            : Date;
  ruoloNelProgetto    : String(200);
}

entity MatchResult {
  key id              : UUID;
  opportunityId       : String(30);
  slotIndex           : Integer;
  risorsaId           : String(20);
  score               : Integer;
  motivazione         : String(2000);
  stato               : String(50);
}

entity PromotionRequest {
  key id              : String(30);
  opportunityId       : String(30);
  opportunityTitolo   : String(200);
  opportunityCliente  : String(200);
  requestedById       : String(20);
  requestedByNome     : String(200);
  requestedAt         : String(50);
  stato               : String(50);
  noteManager         : String(1000);
  noteExecutive       : String(1000);
  reviewedById        : String(20);
  reviewedAt          : String(50);
  risorePerSlot       : String(2000);
}

entity ProjectChangeRequest {
  key id              : String(30);
  projectId           : String(30);
  projectNome         : String(200);
  projectCliente      : String(200);
  requestedById       : String(20);
  requestedByNome     : String(200);
  requestedAt         : String(50);
  stato               : String(50);
  changeType          : String(50);
  payload             : String(2000);
  noteManager         : String(1000);
  noteExecutive       : String(1000);
  reviewedById        : String(20);
  reviewedAt          : String(50);
}
