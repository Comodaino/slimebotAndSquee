{ config, pkgs, ... }:

let 
  pythonEnv = pkgs.python3.withPackages (ps: [
    ps.requests
    ps.python-telegram-bot
  ]);
in

{
  systemd.services.mtgBotService = {
    description = "A scryfall telegram bot";
    after = ["network.target"];
    wantedBy = ["multi-user.target"];
    serviceConfig = {
      EnviromentFile = "/etc/telegram-bot.env";
      ExecStart = "${pythonEnv}/bin/python /etc/nixos/mtgbotservice/mtgbot.py";
      Restart = "always";
      RestartSec = 5;
    };
  };
}
