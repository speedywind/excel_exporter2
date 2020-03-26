call .\.env\Scripts\activate.bat
python .\main.py -c ^
    .\excel_exporter\check_config.json ^
    "\\NAS\Project\Water Gun\产品文档\配置文件"\2.7wg_combination.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.8.1wg_function_gacha.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.8.2wg_function_shop.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.8.3wg_function_signin.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.8.4wg_function_task.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.9wg_mini_game.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.10wg_guild.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.99wg_etc.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.2wg_weapon.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.3.1wg_battle_feature_skill.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.3.2wg_battle_bullet.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.3.3wg_battle_scene.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.3.4wg_battle_monster.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.3.5wg_battle_map.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.4.1wg_roguelike_loot.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.4.3wg_roguelike_event_etc.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.4.4wg_roguelike_raid.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.4.5wg_chapter_stage.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.4.6wg_chapter_episode.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.5.1wg_external_grow_up.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.5.2wg_external_loot.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.5.3wg_external_expedition.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.6.1wg_drama_drama.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.6.2wg_drama_dialogue.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.6.3wg_drama_moment.xlsx ^
	"\\NAS\Project\Water Gun\产品文档\配置文件"\2.6.4wg_drama_event.xlsx ^
    
if exist ..\WaterGun\Assets\LuaFramework\Lua\properties (
	move output\client\lua\*.lua ..\WaterGun\Assets\LuaFramework\Lua\properties
	echo "rsync to ..\WaterGun\Assets\LuaFramework\Lua\properties"
)
pause
